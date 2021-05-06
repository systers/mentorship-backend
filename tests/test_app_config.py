import unittest
import os
from datetime import timedelta

from flask import current_app
from flask_testing import TestCase

from config import BaseConfig
from run import application


class TestTestingConfig(TestCase):
    def create_app(self):
        application.config.from_object("config.TestingConfig")

        secret_key = os.getenv("SECRET_KEY", None)
        application.config["SECRET_KEY"] = (
            secret_key if secret_key else "TEST_SECRET_KEY"
        )
        return application

    def test_app_testing_config(self):
        self.assertIsNotNone(application.config["SECRET_KEY"])
        self.assertFalse(application.config["DEBUG"])
        self.assertTrue(application.config["TESTING"])
        self.assertFalse(application.config["SQLALCHEMY_TRACK_MODIFICATIONS"])
        self.assertEqual("sqlite://", application.config["SQLALCHEMY_DATABASE_URI"])
        self.assertIsNotNone(current_app)

        # testing JWT configurations
        self.assertEqual(
            timedelta(minutes=10), application.config["JWT_ACCESS_TOKEN_EXPIRES"]
        )
        self.assertEqual(
            timedelta(weeks=4), application.config["JWT_REFRESH_TOKEN_EXPIRES"]
        )

    def test_get_bd_uri_function(self):

        expected_result = "db_type_example://db_user_example:db_password_example@db_endpoint_example/db_name_example"
        actual_result = BaseConfig.build_db_uri(
            db_type_arg="db_type_example",
            db_user_arg="db_user_example",
            db_password_arg="db_password_example",
            db_endpoint_arg="db_endpoint_example",
            db_name_arg="db_name_example",
        )
        self.assertEqual(expected_result, actual_result)


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        application.config.from_object("config.DevelopmentConfig")

        secret_key = os.getenv("SECRET_KEY", None)
        application.config["SECRET_KEY"] = (
            secret_key if secret_key else "TEST_SECRET_KEY"
        )

        return application

    def test_app_development_config(self):
        self.assertIsNotNone(application.config["SECRET_KEY"])
        self.assertTrue(application.config["DEBUG"])
        self.assertFalse(application.config["TESTING"])
        self.assertFalse(application.config["SQLALCHEMY_TRACK_MODIFICATIONS"])
        # self.assertEqual('mysql_something', application.config['SQLALCHEMY_DATABASE_URI'])
        self.assertIsNotNone(current_app)

        # testing JWT configurations
        self.assertEqual(
            timedelta(minutes=10), application.config["JWT_ACCESS_TOKEN_EXPIRES"]
        )


class TestStagingConfig(TestCase):
    def create_app(self):
        application.config.from_object("config.StagingConfig")

        secret_key = os.getenv("SECRET_KEY", None)
        application.config["SECRET_KEY"] = (
            secret_key if secret_key else "TEST_SECRET_KEY"
        )

        return application

    def test_app_development_config(self):
        self.assertIsNotNone(application.config["SECRET_KEY"])
        self.assertTrue(application.config["DEBUG"])
        self.assertFalse(application.config["TESTING"])
        self.assertFalse(application.config["SQLALCHEMY_TRACK_MODIFICATIONS"])
        # self.assertEqual('mysql_something', application.config['SQLALCHEMY_DATABASE_URI'])
        self.assertIsNotNone(current_app)

        # testing JWT configurations
        self.assertEqual(
            timedelta(minutes=10), application.config["JWT_ACCESS_TOKEN_EXPIRES"]
        )


class TestLocalConfig(TestCase):
    def create_app(self):
        application.config.from_object("config.LocalConfig")

        secret_key = os.getenv("SECRET_KEY", None)
        application.config["SECRET_KEY"] = (
            secret_key if secret_key else "TEST_SECRET_KEY"
        )
        return application

    def test_app_development_config(self):
        self.assertIsNotNone(application.config["SECRET_KEY"])
        self.assertTrue(application.config["DEBUG"])
        self.assertFalse(application.config["TESTING"])
        self.assertFalse(application.config["SQLALCHEMY_TRACK_MODIFICATIONS"])
        self.assertEqual(
            "sqlite:///local_data.db", application.config["SQLALCHEMY_DATABASE_URI"]
        )
        self.assertIsNotNone(current_app)

        # testing JWT configurations
        self.assertEqual(
            timedelta(minutes=10), application.config["JWT_ACCESS_TOKEN_EXPIRES"]
        )
        self.assertEqual(
            timedelta(weeks=4), application.config["JWT_REFRESH_TOKEN_EXPIRES"]
        )


class TestProductionConfig(TestCase):
    def create_app(self):
        application.config.from_object("config.ProductionConfig")

        secret_key = os.getenv("SECRET_KEY", None)
        application.config["SECRET_KEY"] = (
            secret_key if secret_key else "TEST_SECRET_KEY"
        )

        return application

    def test_app_production_config(self):
        self.assertIsNotNone(application.config["SECRET_KEY"])
        self.assertFalse(application.config["DEBUG"])
        self.assertFalse(application.config["TESTING"])
        self.assertFalse(application.config["SQLALCHEMY_TRACK_MODIFICATIONS"])
        # self.assertEqual('mysql_something', application.config['SQLALCHEMY_DATABASE_URI'])
        self.assertIsNotNone(current_app)

        # testing JWT configurations
        self.assertEqual(
            timedelta(minutes=10), application.config["JWT_ACCESS_TOKEN_EXPIRES"]
        )
        self.assertEqual(
            timedelta(weeks=4), application.config["JWT_REFRESH_TOKEN_EXPIRES"]
        )


if __name__ == "__main__":
    unittest.main()
