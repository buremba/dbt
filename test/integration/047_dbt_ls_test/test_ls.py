from test.integration.base import DBTIntegrationTest, use_profile
from dbt.logger import log_to_stdout, GLOBAL_LOGGER

import json
import os


class TestStrictUndefined(DBTIntegrationTest):

    @property
    def schema(self):
        return 'dbt_ls_047'

    @staticmethod
    def dir(value):
        return os.path.normpath('test/integration/047_dbt_ls_test/' + value)

    @property
    def models(self):
        return self.dir('models')

    @property
    def project_config(self):
        return {
            'analysis-paths': [self.dir('analyses')],
            'archive-paths': [self.dir('archives')],
            'macro-paths': [self.dir('macros')],
            'data-paths': [self.dir('data')],
        }

    def run_dbt_ls(self, args=None, expect_pass=True):
        log_to_stdout(GLOBAL_LOGGER)
        full_args = ['ls']
        if args is not None:
            full_args = full_args + args

        result = self.run_dbt(args=full_args, expect_pass=expect_pass,
                              strict=False, parser=False)

        log_to_stdout(GLOBAL_LOGGER)
        return result

    def assertEqualJSON(self, json_str, expected):
        self.assertEqual(json.loads(json_str), expected)

    def expect_given_output(self, args, expectations):
        for key, values in expectations.items():
            ls_result = self.run_dbt_ls(args + ['--output', key])
            if not isinstance(values, (list, tuple)):
                values = [values]
            self.assertEqual(len(ls_result), len(values))
            for got, expected in zip(ls_result, values):
                if key == 'json':
                    self.assertEqualJSON(got, expected)
                else:
                    self.assertEqual(got, expected)

    def expect_archive_output(self):
        expectations = {
            'name': 'my_archive',
            'selector': 'archive.test.my_archive',
            'json': {
                'name': 'my_archive',
                'package_name': 'test',
                'depends_on': {'nodes': [], 'macros': []},
                'tags': [],
                'config': {
                    'enabled': True,
                    'materialized': 'archive',
                    'post-hook': [],
                    'tags': [],
                    'pre-hook': [],
                    'quoting': {},
                    'vars': {},
                    'column_types': {},
                    'target_database': self.default_database,
                    'target_schema': self.unique_schema(),
                    'unique_key': 'id',
                    'strategy': 'timestamp',
                    'updated_at': 'updated_at'
                },
                'alias': 'my_archive',
                'resource_type': 'archive',
            },
            'path': self.dir('archives/archive.sql'),
        }
        self.expect_given_output(['--resource-type', 'archive'], expectations)

    def expect_analyses_output(self):
        expectations = {
            'name': 'analysis',
            'selector': 'analysis.test.analysis',
            'json': {
                'name': 'analysis',
                'package_name': 'test',
                'depends_on': {'nodes': [], 'macros': []},
                'tags': [],
                'config': {
                    'enabled': True,
                    'materialized': 'view',
                    'post-hook': [],
                    'tags': [],
                    'pre-hook': [],
                    'quoting': {},
                    'vars': {},
                    'column_types': {},
                },
                'alias': 'analysis',
                'resource_type': 'analysis',
            },
            'path': self.dir('analyses/analysis.sql'),
        }
        self.expect_given_output(['--resource-type', 'analysis'], expectations)

    def expect_model_output(self):
        expectations = {
            'name': ('inner', 'outer'),
            'selector': ('model.test.inner', 'model.test.outer'),
            'json': (
                {
                    'name': 'inner',
                    'package_name': 'test',
                    'depends_on': {'nodes': ['model.test.outer'], 'macros': []},
                    'tags': [],
                    'config': {
                        'enabled': True,
                        'materialized': 'view',
                        'post-hook': [],
                        'tags': [],
                        'pre-hook': [],
                        'quoting': {},
                        'vars': {},
                        'column_types': {},
                    },
                    'alias': 'inner',
                    'resource_type': 'model',
                },
                {
                    'name': 'outer',
                    'package_name': 'test',
                    'depends_on': {'nodes': [], 'macros': []},
                    'tags': [],
                    'config': {
                        'enabled': True,
                        'materialized': 'view',
                        'post-hook': [],
                        'tags': [],
                        'pre-hook': [],
                        'quoting': {},
                        'vars': {},
                        'column_types': {},
                    },
                    'alias': 'outer',
                    'resource_type': 'model',
                },
            ),
            'path': (self.dir('models/sub/inner.sql'), self.dir('models/outer.sql')),
        }
        self.expect_given_output(['--resource-type', 'model'], expectations)

    def expect_source_output(self):
        expectations = {
            'name': 'my_source.my_table',
            'selector': 'source:source.test.my_source.my_table',
            'json': {
                'package_name': 'test',
                'name': 'my_table',
                'source_name': 'my_source',
                'resource_type': 'source',
            },
            'path': self.dir('models/schema.yml'),
        }
        # should we do this --select automatically for a user if if 'source' is
        # in the resource types and there is no '--select' or '--exclude'?
        self.expect_given_output(['--resource-type', 'source', '--select', 'source:*'], expectations)

    def expect_seed_output(self):
        expectations = {
            'name': 'seed',
            'selector': 'seed.test.seed',
            'json': {
                'name': 'seed',
                'package_name': 'test',
                'depends_on': {'nodes': [], 'macros': []},
                'tags': [],
                'config': {
                    'enabled': True,
                    'materialized': 'seed',
                    'post-hook': [],
                    'tags': [],
                    'pre-hook': [],
                    'quoting': {},
                    'vars': {},
                    'column_types': {},
                },
                'alias': 'seed',
                'resource_type': 'seed',
            },
            'path': self.dir('data/seed.csv'),
        }
        self.expect_given_output(['--resource-type', 'seed'], expectations)

    def expect_test_output(self):
        expectations = {
            'name': ('not_null_outer_id', 'unique_outer_id'),
            'selector': ('test.test.not_null_outer_id', 'test.test.unique_outer_id'),
            'json': (
                {
                    'name': 'not_null_outer_id',
                    'package_name': 'test',
                    'depends_on': {'nodes': ['model.test.outer'], 'macros': []},
                    'tags': ['schema'],
                    'config': {
                        'enabled': True,
                        'materialized': 'view',
                        'post-hook': [],
                        'severity': 'ERROR',
                        'tags': [],
                        'pre-hook': [],
                        'quoting': {},
                        'vars': {},
                        'column_types': {},
                    },
                    'alias': 'not_null_outer_id',
                    'resource_type': 'test',

                },
                {
                    'name': 'unique_outer_id',
                    'package_name': 'test',
                    'depends_on': {'nodes': ['model.test.outer'], 'macros': []},
                    'tags': ['schema'],
                    'config': {
                        'enabled': True,
                        'materialized': 'view',
                        'post-hook': [],
                        'severity': 'ERROR',
                        'tags': [],
                        'pre-hook': [],
                        'quoting': {},
                        'vars': {},
                        'column_types': {},
                    },
                    'alias': 'unique_outer_id',
                    'resource_type': 'test',
                },
            ),
            'path': (self.dir('models/schema.yml'), self.dir('models/schema.yml')),
        }
        self.expect_given_output(['--resource-type', 'test'], expectations)

    def expect_all_output(self):
        expected_default = {
            'archive.test.my_archive',
            'model.test.inner',
            'model.test.outer',
            'seed.test.seed',
            'source:source.test.my_source.my_table',
            'test.test.not_null_outer_id',
            'test.test.unique_outer_id',
        }
        expected_all = expected_default | {'analysis.test.analysis'}

        results = self.run_dbt_ls(['--resource-type', 'all', '--select', '*', 'source:*'])
        self.assertEqual(set(results), expected_all)

        results = self.run_dbt_ls(['--select', '*', 'source:*'])
        self.assertEqual(set(results), expected_default)

        results = self.run_dbt_ls(['--resource-type', 'default', '--select', '*', 'source:*'])
        self.assertEqual(set(results), expected_default)

        results = self.run_dbt_ls

    def expect_select(self):
        results = self.run_dbt_ls(['--resource-type', 'test', '--select', 'outer'])
        self.assertEqual(set(results), {'test.test.not_null_outer_id', 'test.test.unique_outer_id'})

        self.run_dbt_ls(['--resource-type', 'test', '--select', 'inner'], expect_pass=False)

        results = self.run_dbt_ls(['--resource-type', 'test', '--select', '+inner'])
        self.assertEqual(set(results), {'test.test.not_null_outer_id', 'test.test.unique_outer_id'})

        results = self.run_dbt_ls(['--resource-type', 'model', '--select', 'outer+'])
        self.assertEqual(set(results), {'model.test.outer', 'model.test.inner'})

        results = self.run_dbt_ls(['--resource-type', 'model', '--exclude', 'inner'])
        self.assertEqual(set(results), {'model.test.outer'})

    @use_profile('postgres')
    def test_postgres_ls(self):
        self.expect_archive_output()
        self.expect_analyses_output()
        self.expect_model_output()
        self.expect_source_output()
        self.expect_seed_output()
        self.expect_test_output()
        self.expect_select()
        self.expect_all_output()
