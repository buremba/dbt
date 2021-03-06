import os
from test.integration.base import DBTIntegrationTest, use_profile
from dbt.exceptions import CompilationException


class TestSimpleDependency(DBTIntegrationTest):

    def setUp(self):
        DBTIntegrationTest.setUp(self)
        self.run_sql_file("test/integration/006_simple_dependency_test/seed.sql")

    @property
    def schema(self):
        return "simple_dependency_006"

    @property
    def models(self):
        return "test/integration/006_simple_dependency_test/models"

    @property
    def packages_config(self):
        return {
            "packages": [
                {
                    'git': 'https://github.com/fishtown-analytics/dbt-integration-project',
                    'warn-unpinned': False,
                }
            ]
        }

    @use_profile('postgres')
    def test_postgres_simple_dependency(self):
        self.run_dbt(["deps"])
        results = self.run_dbt(["run"])
        self.assertEqual(len(results),  4)

        self.assertTablesEqual("seed","table_model")
        self.assertTablesEqual("seed","view_model")
        self.assertTablesEqual("seed","incremental")

        self.assertTablesEqual("seed_summary","view_summary")

        self.run_sql_file("test/integration/006_simple_dependency_test/update.sql")

        self.run_dbt(["deps"])
        results = self.run_dbt(["run"])
        self.assertEqual(len(results),  4)

        self.assertTablesEqual("seed","table_model")
        self.assertTablesEqual("seed","view_model")
        self.assertTablesEqual("seed","incremental")

    @use_profile('postgres')
    def test_postgres_simple_dependency_with_models(self):
        self.run_dbt(["deps"])
        results = self.run_dbt(["run", '--models', 'view_model+'])
        self.assertEqual(len(results),  2)

        self.assertTablesEqual("seed","view_model")
        self.assertTablesEqual("seed_summary","view_summary")

        created_models = self.get_models_in_schema()

        self.assertFalse('table_model' in created_models)
        self.assertFalse('incremental' in created_models)

        self.assertEqual(created_models['view_model'], 'view')
        self.assertEqual(created_models['view_summary'], 'view')


class TestSimpleDependencyUnpinned(DBTIntegrationTest):
    def setUp(self):
        DBTIntegrationTest.setUp(self)
        self.run_sql_file("test/integration/006_simple_dependency_test/seed.sql")

    @property
    def schema(self):
        return "simple_dependency_006"

    @property
    def models(self):
        return "test/integration/006_simple_dependency_test/models"

    @property
    def packages_config(self):
        return {
            "packages": [
                {
                    'git': 'https://github.com/fishtown-analytics/dbt-integration-project',
                    'warn-unpinned': True,
                }
            ]
        }

    @use_profile('postgres')
    def test_postgres_simple_dependency(self):
        self.run_dbt(['deps'], strict=False)
        with self.assertRaises(CompilationException):
            self.run_dbt(["deps"])


class TestSimpleDependencyWithDuplicates(DBTIntegrationTest):
    @property
    def schema(self):
        return "simple_dependency_006"

    @property
    def models(self):
        return "test/integration/006_simple_dependency_test/models"

    @property
    def packages_config(self):
        # dbt should convert these into a single dependency internally
        return {
            "packages": [
                {
                    'git': 'https://github.com/fishtown-analytics/dbt-integration-project',
                    'warn-unpinned': False,
                },
                {
                    'git': 'https://github.com/fishtown-analytics/dbt-integration-project.git',
                    'warn-unpinned': False,
                }
            ]
        }

    @use_profile('postgres')
    def test_postgres_simple_dependency_deps(self):
        self.run_dbt(["deps"])


class TestRekeyedDependencyWithSubduplicates(DBTIntegrationTest):
    @property
    def schema(self):
        return "simple_dependency_006"

    @property
    def models(self):
        return "test/integration/006_simple_dependency_test/models"

    @property
    def packages_config(self):
        # dbt-event-logging@0.1.5 requires dbt-utils.git@0.1.12, which the
        # package config handling should detect
        return {
            'packages': [
                {
                    'git': 'https://github.com/fishtown-analytics/dbt-utils',
                    'revision': '0.1.12',
                },
                {
                    'git': 'https://github.com/fishtown-analytics/dbt-event-logging.git',
                    'revision': '0.1.5',
                }
            ]
        }

    @use_profile('postgres')
    def test_postgres_simple_dependency_deps(self):
        self.run_dbt(["deps"])
        self.assertEqual(len(os.listdir('dbt_modules')), 2)


class TestSimpleDependencyBranch(DBTIntegrationTest):

    def setUp(self):
        DBTIntegrationTest.setUp(self)
        self.run_sql_file("test/integration/006_simple_dependency_test/seed.sql")

    @property
    def schema(self):
        return "simple_dependency_006"

    @property
    def models(self):
        return "test/integration/006_simple_dependency_test/models"

    @property
    def packages_config(self):
        return {
            "packages": [
                {
                    'git': 'https://github.com/fishtown-analytics/dbt-integration-project',
                    'revision': 'master',
                    'warn-unpinned': False,
                },
            ]
        }

    def deps_run_assert_equality(self):
        self.run_dbt(["deps"])
        results = self.run_dbt(["run"])
        self.assertEqual(len(results),  4)

        self.assertTablesEqual("seed","table_model")
        self.assertTablesEqual("seed","view_model")
        self.assertTablesEqual("seed","incremental")

        created_models = self.get_models_in_schema()

        self.assertEqual(created_models['table_model'], 'table')
        self.assertEqual(created_models['view_model'], 'view')
        self.assertEqual(created_models['view_summary'], 'view')
        self.assertEqual(created_models['incremental'], 'table')

    @use_profile('postgres')
    def test_postgres_simple_dependency(self):
        self.deps_run_assert_equality()

        self.assertTablesEqual("seed_summary","view_summary")

        self.run_sql_file("test/integration/006_simple_dependency_test/update.sql")

        self.deps_run_assert_equality()

    @use_profile('postgres')
    def test_postgres_empty_models_not_compiled_in_dependencies(self):
        self.deps_run_assert_equality()

        models = self.get_models_in_schema()

        self.assertFalse('empty' in models.keys())
