from boa.interop.System.ExecutionEngine import GetScriptContainer, GetExecutingScriptHash
from boa.interop.Neo.Transaction import Transaction, GetReferences, GetOutputs, GetUnspentCoins
from boa.interop.Neo.Output import GetValue, GetAssetId, GetScriptHash

neo_asset_id = b'\x9b|\xff\xda\xa6t\xbe\xae\x0f\x93\x0e\xbe`\x85\xaf\x90\x93\xe5\xfeV\xb3J\\"\x0c\xcd\xcfn\xfc3o\xc5'

gas_asset_id = b'\xe7-(iy\xeel\xb1\xb7\xe6]\xfd\xdf\xb2\xe3\x84\x10\x0b\x8d\x14\x8ewX\xdeB\xe4\x16\x8bqy,`'


def get_asset_attachments(args):
    """
    Gets information about NEO and Gas attached to an invocation TX

    :return:
        list: A list with information about the tranzaction
    """

    tx = GetScriptContainer()
    references = tx.References

    receiver_addr = GetExecutingScriptHash()
    sender_addr = None
    tokenAmount = args[1] * 100000000

    if len(references) > 0:
        reference = references[0]
        sender_addr = args[0]

    return [receiver_addr, sender_addr, tokenAmount]
