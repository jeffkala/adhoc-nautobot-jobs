"""Nautobot Cloud Secret Update Job."""

import inspect
import os
import json
import requests
from django import forms
from nautobot.extras.jobs import ChoiceVar, Job, ObjectVar, ScriptVariable, StringVar
from nautobot.extras.models import Secret


def fetch_data_from_api(url, api_token, org_id):
    """Make the API call to fetch data from the NBC API."""
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Token {api_token}"
    }
    response = requests.get(url, headers=headers, params={"organization__id=": f"{org_id}"}, timeout=30)
    if response.status_code == 200:
        data = response.json()["results"]
        choices = [(item["id"], item["name"]) for item in data]
        return choices


class CloudSecretRotationv1(Job):
    """Nautobot Cloud secrets rotation."""
    nbc_org_id = StringVar()
    nbc_api_token = StringVar(widget=forms.PasswordInput())
    new_secret_value = StringVar(widget=forms.PasswordInput())
    secret_description = StringVar()
    nautobot_cloud_secret = StringVar()

    class Meta:
        """Job details."""
        name = "Rotate a Cloud Secret v1"
        description = "Job to perform a Nautobot Cloud Secrets Rotation v1."
        has_sensitive_variables = True
        hidden = False

    def run(self, *args, **data):  # pylint: disable=too-many-branches
        """Run queries against Nautobot cloud and rotate secret values."""
        get_secret_url = f"https://nautobot.cloud/api/secret/{data['nautobot_cloud_secret']}/"
        request_data = {
            "secret_value": {
                f"{data['nautobot_cloud_secret']}": f"{data['new_secret_value']}"
                }, "description": f"{data['secret_description']}"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Token {data['nbc_api_token']}"
        }
        result = requests.patch(get_secret_url, headers=headers, data=json.dumps(request_data), timeout=30)
        self.logger.info(result.json())


class CloudSecretRotationv2(Job):
    """Nautobot Cloud secrets rotation."""
    #nbc_org_id = StringVar()
    #nbc_api_token = StringVar(widget=forms.PasswordInput())
    new_secret_value = StringVar(widget=forms.PasswordInput())
    secret_description = StringVar()
    # nautobot_cloud_api_token = ObjectVar(model=Secret, queryset=Secret.objects.all())
    # nautobot_cloud_secret = Future Get automatically joined from _get_vars overload
    # nautobot_cloud_secret = StringVar()

    class Meta:
        """Job details."""
        name = "Rotate a Cloud Secret v2"
        description = "Job to perform a Nautobot Cloud Secrets Rotation v2."
        has_sensitive_variables = True
        hidden = False

    @classmethod
    def _get_vars(cls):
        """
        Return dictionary of ScriptVariable attributes defined on this class or any of its base parent classes.
        The variables are sorted in the order that they were defined,
        with variables defined on base classes appearing before subclass variables.
        """
        cls_vars = {}
        # get list of base classes, including cls, in reverse method resolution order: [BaseJob, Job, cls]
        base_classes = reversed(inspect.getmro(cls))
        attr_names = [name for base in base_classes for name in base.__dict__.keys()]
        for name in attr_names:
            attr_class = getattr(cls, name, None).__class__
            if name not in cls_vars and issubclass(attr_class, ScriptVariable):
                cls_vars[name] = getattr(cls, name)
                # NOTE this is overloaded classmethod from Job base class to inject on-demand choices from NBC.
                # This next line is the only difference from the inherited class method.
                cls_vars.update(
                    {
                        "nautobot_cloud_secret": ChoiceVar(
                            choices=fetch_data_from_api(
                                "https://nautobot.cloud/api/secret/",
                                api_token=os.getenv('NBC_TOKEN'),
                                org_id=os.getenv('NBC_ORG_ID'),
                            )
                        )
                    }
                )
        return cls_vars

    def run(self, *args, **data):  # pylint: disable=too-many-branches
        """Run queries against Nautobot cloud and rotate secret values."""
        get_secret_url = f"https://nautobot.cloud/api/secret/{data['nautobot_cloud_secret']}/"
        request_data = {
            "secret_value": {
                f"{data['nautobot_cloud_secret']}": f"{data['new_secret_value']}"
                }, "description": f"{data['secret_description']}"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Token {os.getenv('NBC_TOKEN')}"
        }
        result = requests.patch(get_secret_url, headers=headers, data=json.dumps(request_data), timeout=30)
        self.logger.info(result.json())
