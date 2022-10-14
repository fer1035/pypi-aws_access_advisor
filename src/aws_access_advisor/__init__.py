"""Parse AWS Access Advisor output."""
import json
import time
import argparse
import boto3
import aws_ssooidc as sso


__version__ = "2022.10.1.4"


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
    entity_arn: str,
    profile_name: str = None,
    access_key_id: str = None,
    secret_access_key: str = None,
    sso_url: str = None,
    sso_role_name: str = None,
    sso_account_id: str = None,
) -> dict:
    """
    Generate and download AWS Access Advisor report for ARN.

    return dict
    """
    if profile_name is not None:
        session = boto3.Session(profile_name=profile_name)
    elif access_key_id is not None and secret_access_key is not None:
        access_key_id = access_key_id
        secret_access_key = secret_access_key
        session = boto3.Session(
            aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key
        )
    elif (
        sso_role_name is not None and sso_url is not None and sso_account_id is not None
    ):
        auth = login(sso_account_id, sso_url, sso_role_name)
        access_key_id = auth["roleCredentials"]["accessKeyId"]
        secret_access_key = auth["roleCredentials"]["secretAccessKey"]
        session_token = auth["roleCredentials"]["sessionToken"]
        session = boto3.Session(
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            aws_session_token=session_token,
        )
    else:
        raise Exception("Invalid authentication parameter(s)")

    client = session.client("iam")
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


def parse(report: dict) -> list:
    """
    Parse AWS Access Advisor report.

    return list
    """
    actions = []
    for obj in report["ServicesLastAccessed"]:
        try:
            for obj_in in obj["TrackedActionsLastAccessed"]:
                actions.append(
                    f'{obj["ServiceNamespace"]}:{obj_in["ActionName"]}'
                )
        except Exception as e:
            actions.append(f'{obj["ServiceNamespace"]}:*')
    return actions


def get_params():
    """Get parameters from script input."""
    myparser = argparse.ArgumentParser(
        add_help=True,
        allow_abbrev=False,
        description="Generate AWS Access Advisor IAM policy actions.",
        usage="%(prog)s [options]",
    )
    myparser.add_argument(
        "-v", "--version", action="version", version="%(prog)s 2122.10.1.9"
    )
    myparser.add_argument(
        "-e",
        "--entity_arn",
        action="store",
        help="AWS entity role ARN for access report generation.",
        required=True,
        type=str,
    )
    myparser.add_argument(
        "-p",
        "--profile_name",
        action="store",
        help="AWSCLI profile name for authenticating with a profile.",
        nargs="?",
        default=None,
        required=False,
        type=str,
    )
    myparser.add_argument(
        "-k",
        "--access_key_id",
        action="store",
        help="AWSCLI IAM access key ID for authenticating with an IAM user.",
        nargs="?",
        default=None,
        required=False,
        type=str,
    )
    myparser.add_argument(
        "-s",
        "--secret_access_key",
        action="store",
        help="AWSCLI IAM secret access key for authenticating with an IAM user.",
        nargs="?",
        default=None,
        required=False,
        type=str,
    )
    myparser.add_argument(
        "-a",
        "--sso_account_id",
        action="store",
        help="AWS account ID for authenticating with AWS SSO.",
        nargs="?",
        default=None,
        required=False,
        type=str,
    )
    myparser.add_argument(
        "-r",
        "--sso_role_name",
        action="store",
        help="AWS SSO role name for authenticating with AWS SSO.",
        nargs="?",
        default=None,
        required=False,
        type=str,
    )
    myparser.add_argument(
        "-u",
        "--sso_url",
        action="store",
        help="AWS SSO login URL for authenticating with AWS SSO.",
        nargs="?",
        default=None,
        required=False,
        type=str,
    )
    args = myparser.parse_args()
    return args


def main():
    """Execute module as a script."""
    params = get_params()
    report = get_report(
        params.entity_arn,
        profile_name=params.profile_name,
        access_key_id=params.access_key_id,
        secret_access_key=params.secret_access_key,
        sso_url=params.sso_url,
        sso_role_name=params.sso_role_name,
        sso_account_id=params.sso_account_id,
    )
    print(
        f'Job status: {report["JobStatus"]} after {report["processing_time"]} second(s).'
    )
    print("\n".join(parse(report)))
