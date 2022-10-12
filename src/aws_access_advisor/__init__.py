r"""
Parse AWS Access Advisor output.

Prerequisite dependencies:
    1. boto3: https://pypi.org/project/boto3/
    2. aws-ssooidc: https://pypi.org/project/aws-ssooidc/
    3. SSO access to the target account with sufficient privileges.

Execute as a function:
    import <file_name_without_.py>
    auth = <file_name_without_.py>.login("<account_id>", "<sso_url>", "<admin_role_name>")
    report = <file_nafile_name_without_.pyme>.get_report(
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

Execute as a script:
    python <file_name_with_.py> \
    -a <account_id> \
    -e <entity_role_arn> \
    -r <admin_role_name> \  # [OPTIONAL]
    -u <sso_url> \  # [OPTIONAL]
    > <output_path>
"""
import json
import time
import argparse
import boto3
import aws_ssooidc as sso


__version__ = '2022.10.1.2'


def login(account_id: str, url: str, admin_role: str) -> dict:
    """
    Login to AWS account through SSO.

    return dict
    """
    access_token = sso.gettoken(url)["accessToken"]
    client = boto3.client("sso")
    response_login = client.get_role_credentials(
        roleName=admin_role, accountId=account_id, accessToken=access_token
    )
    return response_login


def get_report(
    entity_arn: str, access_key_id: str, secret_access_key: str, session_token: str
) -> dict:
    """
    Generate and download AWS Access Advisor report for ARN.

    return dict
    """
    client = boto3.client(
        "iam",
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        aws_session_token=session_token,
    )
    response_job = client.generate_service_last_accessed_details(
        Arn=entity_arn, Granularity="ACTION_LEVEL"
    )
    counter = 0
    job_status = "IN_PROGRESS"
    while job_status == "IN_PROGRESS" and counter < 10:
        response_report = client.get_service_last_accessed_details(
            JobId=response_job["JobId"]
        )
        job_status = response_report["JobStatus"]
        counter += 1
        time.sleep(1)
    response_report["processing_time"] = counter
    return response_report


if __name__ == "__main__":

    myparser = argparse.ArgumentParser(
        add_help=True,
        allow_abbrev=False,
        description="Generate AWS Access Advisor IAM policy actions.",
        usage="%(prog)s [options]",
    )
    myparser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.0")
    myparser.add_argument(
        "-a",
        "--account_id",
        action="store",
        help="AWS account ID",
        required=True,
        type=str,
    )
    myparser.add_argument(
        "-e",
        "--entity",
        action="store",
        help="AWS entity role ARN",
        required=True,
        type=str,
    )
    myparser.add_argument(
        "-r",
        "--role",
        action="store",
        help="AWS admin role ARN",
        required=False,
        type=str,
    )
    myparser.add_argument(
        "-u",
        "--url",
        action="store",
        help="AWS SSO login URL",
        required=False,
        type=str,
    )
    args = myparser.parse_args()

    auth = login(args.account_id, args.url, args.role)
    report = get_report(
        args.entity,
        auth["roleCredentials"]["accessKeyId"],
        auth["roleCredentials"]["secretAccessKey"],
        auth["roleCredentials"]["sessionToken"],
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
