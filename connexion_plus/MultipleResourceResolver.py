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

        def get_controller_name():
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
                if s and pattern.search(s) is None:
                    resource_name += s.title()

            if x_router_controller:
                name = x_router_controller

            elif resource_name:
                resource_controller_name = resource_name.replace('-', '_')
                name += '.' + resource_controller_name

            return name

        def get_function_name():
            method = operation.method

            is_collection_endpoint = \
                method.lower() == 'get' \
                and path_match.group('resource_name') \
                and not path_match.group('extended_path')

            return self.collection_endpoint_name if is_collection_endpoint else method.lower()

        return '{}.{}'.format(get_controller_name(), get_function_name())
