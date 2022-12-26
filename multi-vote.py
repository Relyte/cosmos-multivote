import argparse
import json

from subprocess import run
from time import sleep, strftime
from getpass import getpass


def parseArgs():
    """Parse and return argparse arguments"""
    parser = argparse.ArgumentParser(
        description="Create json file for multiple votes in a single transaction"
    )
    parser.add_argument(
        "--denom",
        dest="denom",
        required=False,
        default="ukuji",
        help="native chain denom",
    )
    parser.add_argument(
        "--daemon",
        dest="daemon",
        required=False,
        default="kujirad",
        help="daemon for sending tx",
    )
    parser.add_argument(
        "-c",
        "--chain_id",
        dest="chain_id",
        required=False,
        default="cosmoshub-4",
        help="Chain ID (ex. kaiyo-1)",
    )
    parser.add_argument(
        "-e",
        "--endpoint",
        dest="endpoint",
        required=False,
        help="RPC endpoint",
    )
    parser.add_argument(
        "-m",
        "--memo",
        dest="memo",
        help="Memo to send with votes",
    )
    parser.add_argument(
        "-k",
        "--keyname",
        dest="keyname",
        required=False,
        help="Wallet to vote from",
    )
    parser.add_argument(
        "-b",
        "--keyringbackend",
        dest="keyringbackend",
        default="test",
        required=False,
        help="Keyring Backend type",
    )
    parser.add_argument(
        "-s",
        "--send_address",
        dest="send_address",
        required=True,
        help="Address to vote from",
    )
    parser.add_argument(
        "-v",
        "--vote",
        dest="vote",
        action="append",
        required=True,
        help="Votes in the format of `proposal_id:vote_option` (eg: 110:no 111:yes 112:veto 113:abstain)",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        dest="dryrun",
        default=False,
        required=False,
        action="store_true",
        help="Do not sign or broadcast tx, just prepare the .json file",
    )
    return parser.parse_args()


def buildVoteJSON(send_address: str, denom: str, memo: str, votes: list) -> dict:
    """Creates a JSON object containing the body, auth_info, and signatures of an unsigned transaction"""
    data = {
        "body": {
            "messages": [],
            "memo": memo,
            "timeout_height": "0",
            "extension_options": [],
            "non_critical_extension_options": [],
        },
        "auth_info": {
            "signer_infos": [],
            "fee": {
                "amount": [{"denom": denom, "amount": "50000"}],
                "gas_limit": "1500000",
                "payer": "",
                "granter": "",
            },
        },
        "signatures": [],
    }
    message_list = []
    for vote in votes:
        message = {
            "@type": "/cosmos.gov.v1beta1.MsgVote",
            "proposal_id": vote["proposal_id"],
            "voter": send_address,
            "option": vote["vote_option"],
        }
        message_list.append(message)
    data["body"]["messages"] = message_list
    return data


def buildVoteTX(
    send_address: str, denom: str, daemon: str, memo: str, votes: list, timestamp: str
):
    """Builds a .json file containing the full unsigned vote transaction"""
    tx_json_data = buildVoteJSON(
        send_address=send_address, denom=denom, memo=memo, votes=votes
    )
    with open(f"/tmp/{daemon}_{timestamp}_vote.json", "w+") as f:
        f.write(json.dumps(tx_json_data))
        f.close()


def buildVoteList(input_votes: list) -> list:
    """Takes a list of votes and returns them in dict format after converting the vote_options"""
    vote_dict_list = []
    for vote in input_votes:
        tmp_vote = {}
        tmp_vote["proposal_id"] = vote.split(":")[0]
        tmp_vote["vote_option"] = convertVoteOptions(vote.split(":")[1])
        vote_dict_list.append(tmp_vote)
    return vote_dict_list


def convertVoteOptions(vote: str) -> str:
    """Convers vote options into their proper syntax"""
    # TODO: Use match in place of if/elif once Python 3.10 is more common.
    if vote.casefold() == "yes".casefold():
        vote = "VOTE_OPTION_YES"
    elif vote.casefold() == "no".casefold():
        vote = "VOTE_OPTION_NO"
    elif vote.casefold() == "abstain".casefold():
        vote = "VOTE_OPTION_ABSTAIN"
    elif vote.casefold() == "veto".casefold():
        vote = "VOTE_OPTION_NO_WITH_VETO"
    else:
        vote = "VOTE_OPTION_UNSPECIFIED"
    return vote


def sign_and_broadcast(
    daemon: str,
    chain_id: str,
    keyname: str,
    node: str,
    keyringbackend: str,
    timestamp: str,
):
    """Signs and broadcasts the unsigned transaction json using the chain daemon"""
    print(
        f"Signing /tmp/{daemon}_{timestamp}_vote.json as ~/{daemon}_{timestamp}_vote_signed.json"
    )
    keypass = getpass(prompt="Enter keyring passphrase: ")
    result = run(
        f"{daemon} tx sign /tmp/{daemon}_{timestamp}_vote.json --from {keyname} -ojson --output-document ~/{daemon}_{timestamp}_vote_signed.json --node {node} --chain-id {chain_id} --keyring-backend {keyringbackend}",
        stdin=keypass,
        shell=True,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    print(result.stderr)
    sleep(1)
    print(
        f"Sending ~/{daemon}_{timestamp}_vote_signed.json to {node} for chain {chain_id}"
    )
    result = run(
        f"{daemon} tx broadcast ~/{daemon}_{timestamp}_vote_signed.json --node {node} --chain-id {chain_id}",
        shell=True,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    print(result.stderr)


def main():
    """Run the funtions in order for typical use"""
    args = parseArgs()
    denom = args.denom
    daemon = args.daemon
    chain_id = args.chain_id
    endpoint = args.endpoint
    send_address = args.send_address
    memo = args.memo
    keyname = args.keyname
    keyringbackend = args.keyringbackend
    votes = args.vote
    dryrun = args.dryrun

    timestr = strftime("%Y%m%d-%H%M%S")
    vote_dict_list = buildVoteList(votes)
    buildVoteTX(
        send_address=send_address,
        denom=denom,
        daemon=daemon,
        memo=memo,
        timestamp=timestr,
        votes=vote_dict_list,
    )
    if not dryrun:
        sign_and_broadcast(
            daemon=daemon,
            timestamp=timestr,
            chain_id=chain_id,
            keyname=keyname,
            node=endpoint,
            keyringbackend=keyringbackend,
        )


if __name__ == "__main__":
    main()
