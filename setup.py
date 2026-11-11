import setuptools

with open('README.md', 'r') as fh:
	long_description = fh.read()

setuptools.setup(
	name='printipy',
	version='1.3.0',
	author='Lawrence Weikum',
	description='Printify API for Python',
	url='https://github.com/lawrencemq/printipy',
	keywords=['printify', 'print on demand', 'api'],
	long_description=long_description,
	long_description_content_type='text/markdown',
	classifiers=[
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.11',
		'Programming Language :: Python :: 3.12',
		'Programming Language :: Python :: 3.13',
		'Programming Language :: Python :: 3.14',
		'Programming Language :: Python :: 3.15',
		'Topic :: Internet',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
	],
	python_requires='>=3.11',
	py_modules=['printipy'],
	packages=setuptools.find_packages(exclude=['*tests*']),
	install_requires=['requests>=2.33.0', 'dataclasses-json'],
)
