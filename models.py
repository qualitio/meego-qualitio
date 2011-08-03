from django.db import models
from qualitio.core.custommodel.models import ModelCustomization
from django.core.exceptions import ValidationError

# import store models
from qualitio.store.models import TestCaseDirectory, TestCase

# import execute models
from qualitio.execute.models import TestRun

class MeegoTestCaseDirectory(ModelCustomization):
    is_suite = models.BooleanField(default=False)

    def clean_origin(self):
        for ancestor in self.origin.get_ancestors():
            if ancestor.customization.is_suite:
                raise ValidationError('Parent directory is already a suite')

    class Meta:
        model = TestCaseDirectory

class MeegoTestCase(ModelCustomization):
    FEATURE_TYPE_CHOICES = (
        ('Basic', 'Basic'),
        ('Advanced', 'Advanced'),
    )

    feature_type = models.CharField(max_length=32, choices=FEATURE_TYPE_CHOICES, default='Basic')

    def resolve_suite(self):
        if self.origin.parent.customization.is_suite:
            return self.origin.parent.name
        for directory in self.origin.parent.get_ancestors():
            if directory.customization.is_suite:
                return directory.name
        return "Test Suite" #default name

    class Meta:
        model = TestCase

class MeegoTestRun(ModelCustomization):
    hwbuild = models.CharField(max_length=256, blank=True, null=True)
    hwproduct = models.CharField(max_length=256, blank=True, null=True)

    def calculate_set_name(self):
        set_list = []
        for test_case in self.origin.testcases.all():
            set_list.append(test_case.origin.customization.feature_type)
        if set_list:
            return list(set(set_list))[0] #ToDo: change it later to sth better
        return "Basic"

    def calculate_suite_name(self):
        """Returns the suite name for the set of test cases"""
        # ToDo: implement some simple algorithm that
        # iterates through test case runs in the test run and
        # checks the directory of the test case from store
        # corresponding to the test case run
        # for now returns string
        suite_list = []
        for test_case in self.origin.testcases.all():
            suite_list.append(test_case.origin.customization.resolve_suite())
        if suite_list:
            return list(set(suite_list))[0] #ToDo: change it later to sth better
        return "Test Suite"

    class Meta:
        model = TestRun

