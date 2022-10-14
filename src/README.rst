======================
**aws-access-advisor**
======================

Overview
--------

Generate IAM actions list from AWS Access Advisor reports.

Prerequisites
-------------

- *Python >= 3.6*
- *aws-ssooidc (https://pypi.org/project/aws-ssooidc/) >= 2021.1.1.1*
- *boto3 (https://pypi.org/project/boto3/) >= 1.17.78*

Required Arguments
------------------

- AWS entity ARN (role, user, etc. to use for report generation)

Optional Arguments
------------------

If authenticating with named profiles:

- AWSCLI profile name

If authenticating with IAM acccess key credentials:

- AWS access key id
- AWS secret access key

If authenticating with SSO:

- AWS account ID
- AWS SSO Permission Set (role) name
- AWS SSO login URL

Usage
-----

Installation:

.. code-block:: BASH

   pip3 install aws-access-advisor
   # or
   python3 -m pip install aws-access-advisor

In Python3 authenticating with named profiles:

.. code-block:: BASH

   import aws_access_advisor as access

   report = access.get_report(
      "<entity_arn>",
      profile_name="<profile_name>",
    )
   print(
      f'Job status: {report["JobStatus"]} after {report["processing_time"]} second(s).'
   )
   print("\n".join(access.parse(report)))

In Python3 authenticating with IAM access key credentials:

.. code-block:: BASH

   import aws_access_advisor as access

   report = access.get_report(
      "<entity_arn>",
      access_key_id="<access_key_id>",
      secret_access_key="<secret_access_key>",
    )
   print(
      f'Job status: {report["JobStatus"]} after {report["processing_time"]} second(s).'
   )
   print("\n".join(access.parse(report)))

In Python3 authenticating with SSO:

.. code-block:: BASH

   import aws_access_advisor as access

   report = access.get_report(
      "<entity_arn>",
      sso_url="<sso_url>",
      sso_role_name="<sso_role_name>",
      sso_account_id="<sso_account_id>",
    )
   print(
      f'Job status: {report["JobStatus"]} after {report["processing_time"]} second(s).'
   )
   print("\n".join(access.parse(report)))

In BASH authenticating with named profiles:

.. code-block:: BASH

   python [/path/to/module/]aws_access_advisor \
   -e <entity_arn> \
   -p <profile_name>

In BASH authenticating with IAM access key credentials:

.. code-block:: BASH

   python [/path/to/module/]aws_access_advisor \
   -e <entity_arn> \
   -k <access_key_id> \
   -s <secret_access_key>

In BASH authenticating with SSO:

.. code-block:: BASH

   python [/path/to/module/]aws_access_advisor \
   -e <entity_arn> \
   -a <sso_account_id> \
   -r <sso_role_name> \
   -u <sso_url>
