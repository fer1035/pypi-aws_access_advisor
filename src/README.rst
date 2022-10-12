======================
**aws-access-advisor**
======================

Overview
--------

Generate IAM actions list from AWS Access Advisor reports.

Prerequisites
-------------

- *Python >= 3.6*
- *[aws-ssooidc](https://pypi.org/project/aws-ssooidc/) >= 2021.1.1.1*
- *[boto3](https://pypi.org/project/boto3/) >= 1.17.78*

Required Arguments
------------------

- AWS account ID
- AWS entity ARN (role, user, etc. to use for report generation)
- AWS SSO Permission Set (admin role) name for login purposes
- AWS SSO login URL

Usage
-----

Installation:

.. code-block:: BASH

   pip3 install aws-access-advisor
   # or
   python3 -m pip install aws-access-advisor

In Python3:

.. code-block:: BASH

   import aws_access_advisor as access
   auth = access.login("<account_id>", "<sso_url>", "<admin_role_name>")
   report = access.get_report(
      "<entity_role_arn>",
      auth["roleCredentials"]["accessKeyId"],
      auth["roleCredentials"]["secretAccessKey"],
      auth["roleCredentials"]["sessionToken"]
   )
   print(
      f'Job status: {report["JobStatus"]} after {report["processing_time"]} second(s).'
   )
   for obj in report["ServicesLastAccessed"]:
      if "LastAuthenticatedEntity" in obj:
         try:
               for obj_in in obj["TrackedActionsLastAccessed"]:
                  if "LastAccessedEntity" in obj_in:
                     print(f'"{obj["ServiceNamespace"]}:{obj_in["ActionName"]}",')
         except Exception as e:
               print(f'"{obj["ServiceNamespace"]}:*",')

In BASH:

.. code-block:: BASH

   python [/path/to/module/]__init__.py \
   -a <account_id> \
   -e <entity_role_arn> \
   -r <admin_role_name> \  # [OPTIONAL]
   -u <sso_url> \  # [OPTIONAL]
   > <output_path>
