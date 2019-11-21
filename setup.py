#from distutils.core import setup
from setuptools import setup

with open('README.md', encoding='utf-8') as f:
    readme = f.read()

setup(
  name = 'connexion-plus',      
  packages = ['connexion_plus'], 
  version = '0.24',
  license='MIT', 
  description = 'Connexion with benefits for microservices',
  long_description=readme,
  long_description_content_type='text/markdown',
  author = 'Peter Heiss',
  author_email = 'peter.heiss@uni-muenster.de',
  url = 'https://github.com/Heiss/connexion-plus',
  keywords = ['connexion', 'microservice', 'tracing', 'prometheus', 'jaeger'],
  python_requires='>=3.6',
  install_requires=[    
          'connexion',
          'jaeger-client',
          'prometheus-flask-exporter',
          'requests',
          'opentracing-instrumentation',
          'Flask-Opentracing',
          'htmlmin',
          'flask-cors'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)
