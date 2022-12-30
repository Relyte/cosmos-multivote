# Cosmos Multivote

This application aims to help validators submit multiple vote transactions in a single transaction. This alleviates a lot of the annoyance of using a hardware wallet and having 10+ proposals that need to be voted on (Kujira).

## Usage

Clone the repo:

```
git clone https://github.com/Relyte/cosmos-multivote
```

Run the application with the desired parameters (see [Available Parameters](#available-parameters)):

```
python3 multi-vote.py --denom denom --daemon daemon -c chain-id -m "Memo" -k key_name -b backend -s sender_address -v prop_id1:yes -v prop_id2:yes -e rpc_endpoint
```

A full example that generated the following tx:
https://ping.pub/kujira/tx/C1FAD96AF8E517144E12570C851B8405CEC076FF51A2196D3491823B2FD35C0E

```
python3 multi-vote.py --denom ukuji --daemon kujirad -c kaiyo-1 -m "Test Multi-Vote" -k relyte -b os -s kujira1tfknxt857r4lm8eh2py5n3yq00t3mq5eerh6qs -v 127:yes -v 128:yes -v 129:yes -e https://kujira.rpc.kjnodes.com:443
```

### Aliasing for easy usage

The base part of the command can be aliased to avoid having to remember it each time. Notably, the RPC server can be included in this. In your `.profile`, `.bashrc`, etc. add the following, replacing the parameters as needed:

```
alias mvkujira="python3 $HOME/cosmos-multivote/multi-vote.py --denom ukuji --daemon kujirad -c kaiyo-1 -k relyte -b os -s kujira1tfknxt857r4lm8eh2py5n3yq00t3mq5eerh6qs -e https://kujira.rpc.kjnodes.com:443"
```

The alias command, `mvkujira`, can be replaced with whatever name you prefer for the alias. For ease of use, I use `mv${chain_name}` as the alias. The full path to the `multi-vote.py` script should be included in the alias.

After this is done, run the following, replacing `.profile` with the file that was previously edited:

```
source ~/.profile
```

Once this is done, you can now use the `mvkujira` command to make the process easier:

```
mvkujira -v 134:yes -v 135:yes -m "mvkujira multi-vote tx memo"
```

### Available Parameters

|short|long|default|help|
| :--- | :--- | :--- | :--- |
|`-h`|`--help`||show this help message and exit|
||`--denom`|`ukuji`|native chain denom|
||`--daemon`|`kujirad`|daemon for sending tx|
|`-c`|`--chain_id`|`kaiyo-1`|Chain ID (ex. kaiyo-1)|
|`-e`|`--endpoint`|`None`|RPC endpoint|
|`-m`|`--memo`|`None`|Memo to send with votes|
|`-k`|`--keyname`|`None`|Wallet to vote from|
|`-b`|`--keyringbackend`|`test`|Keyring Backend type|
|`-s`|`--send_address`|`None`|Address to vote from|
|`-v`|`--vote`|`None`|Votes in the format of `proposal_id:vote_option` (eg: 110:no 111:yes 112:veto 113:abstain)|
|`-d`|`--dry-run`|`False`|Do not sign or broadcast tx, just prepare the .json file|