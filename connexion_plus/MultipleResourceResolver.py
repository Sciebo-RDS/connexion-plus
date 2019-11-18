import re, string
import sys
from connexion.resolver import RestyResolver, Resolution
from connexion.exceptions import ResolverError

class MultipleResourceResolver(RestyResolver):
    def resolve(self, operation):
        """
        Default operation resolver
        :type operation: connexion.operations.AbstractOperation
        """

        # set randomizer to not collide endpoint_names, so that parameters for resources are possible.
        # Otherwise the following example collides:
        #   /res1 [GET] and /res1/{id} [GET]
        operation._randomize_endpoint = 2

        operation_id = self.resolve_operation_id(operation)
        try:
            return Resolution(self.resolve_function_from_operation_id(operation_id), operation_id)
        except ResolverError:
            return Resolution(self.resolve_function_from_operation_id(operation_id.lower()), operation_id)
            

    def resolve_operation_id_using_rest_semantics(self, operation):
        """
        Resolves the operationId using REST semantics without collision for longer paths with multiple ressources
        :type operation: connexion.operations.AbstractOperation
        """
        path_match = re.search(
            r'^/?(?P<resource_name>([\w\-](?<!/))*)(?P<trailing_slash>/*)(?P<extended_path>.*)$', operation.path
        )

        count_resource = 0
        count_parameters = 0

        def get_controller_name():
            nonlocal count_parameters, count_resource
            x_router_controller = operation.router_controller

            #chars = re.escape(string.punctuation)
            #resource_name = re.sub(r'[' + chars + ']', '_', operation.path)

            # empty name to append to

            name = self.default_module_name
            resource_name = ''
            # split path at slash to separate every parameter
            split = re.split("/", operation.path)
            for s in split:
                # find the parameter, where a variable was defined to exlude it in resource_name
                pattern = re.compile(r"\{[a-zA-Z-_]+\}")
                if s:
                    if pattern.search(s) is None:
                        count_resource += 1 # count up the founded resource
                        resource_name += s.title()
                    else:
                        count_parameters += 1

            if x_router_controller:
                name = x_router_controller

            elif resource_name:
                resource_controller_name = resource_name.replace('-', '_')
                name += '.' + resource_controller_name

            return name

        def get_function_name():
            nonlocal count_parameters, count_resource
            method = operation.method

            is_collection_endpoint = \
                method.lower() == 'get' \
                and count_resource > count_parameters

            return self.collection_endpoint_name if is_collection_endpoint else method.lower()

        return '{}.{}'.format(get_controller_name(), get_function_name())

