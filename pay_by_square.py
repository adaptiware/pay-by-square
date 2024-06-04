import lzma
import binascii
from typing import Optional, List, Union
from datetime import datetime, date


def generate(
    *,
    amount: float,
    iban: Union[str, List[Union[str, List[str]]]],
    swift: str = '',
    date: Optional[date] = None,
    beneficiary_name: str = '',
    currency: str = 'EUR',
    variable_symbol: str = '',
    constant_symbol: str = '',
    specific_symbol: str = '',
    note: str = '',
    beneficiary_address_1: str = '',
    beneficiary_address_2: str = '',
) -> str:
    '''Generate pay-by-square code that can be used to create a QR code for
    banking apps.

    If the date is not provided, the current date will be used.

    The 'iban' parameter can be provided in the following formats:
    1. A single string representing an IBAN.
    2. A list of strings, each representing an IBAN.
    3. A list of lists, where each sublist contains an IBAN and an optional SWIFT code.

    Note: If you provide the 'iban' parameter as a list, the SWIFT codes will be handled
    separately from the 'swift' parameter, which will then be ignored.
    The maximum number of IBANs allowed is 5.
    '''

    if date is None:
        date = datetime.now()

    # Handle single IBAN or list of IBANs
    ibans_list = []
    if isinstance(iban, list):
        if len(iban) > 5:
            raise ValueError("A maximum of 5 IBANs are allowed.")
        for entry in iban:
            if isinstance(entry, list):
                ibans_list.append((entry[0], entry[1] if len(entry) > 1 else ''))
            elif isinstance(entry, str):
                ibans_list.append((entry, ''))
            else:
                raise ValueError("Invalid IBAN entry format.")
        num_accounts = len(ibans_list)
    else:
        ibans_list.append((iban, swift))
        num_accounts = 1

    # 1) create the basic data structure
    data_parts = [
        '',
        '1',  # payment
        '1',  # simple payment
        f'{amount:.2f}',
        currency,
        date.strftime('%Y%m%d'),
        variable_symbol,
        constant_symbol,
        specific_symbol,
        '',  # previous 3 entries in SEPA format, empty because already provided above
        note,
        str(num_accounts),  # number of accounts
    ]

    # Add IBANs and SWIFT pairs
    for iban, swift in ibans_list:
        data_parts.append(iban)
        data_parts.append(swift)

    data_parts.extend([
        '0',  # not recurring
        '0',  # not 'inkaso'
        beneficiary_name,
        beneficiary_address_1,
        beneficiary_address_2,
    ])

    data = '\t'.join(data_parts)

    # 2) Add a crc32 checksum
    checksum = binascii.crc32(data.encode()).to_bytes(4, 'little')
    total = checksum + data.encode()

    # 3) Run through XZ
    compressed = lzma.compress(
        total,
        format=lzma.FORMAT_RAW,
        filters=[
            {
                'id': lzma.FILTER_LZMA1,
                'lc': 3,
                'lp': 0,
                'pb': 2,
                'dict_size': 128 * 1024,
            }
        ],
    )

    # 4) prepend length and convert to hex
    compressed_with_length = b'\x00\x00' + len(total).to_bytes(2, 'little') + compressed

    # 5) Convert to padded binary string
    binary = ''.join(
        [bin(single_byte)[2:].zfill(8) for single_byte in compressed_with_length]
    )

    # 6) Pad with zeros on the right up to a multiple of 5
    length = len(binary)
    remainder = length % 5
    if remainder:
        binary += '0' * (5 - remainder)
        length += 5 - remainder

    # 7) Substitute each quintet of bits with corresponding character
    subst = '0123456789ABCDEFGHIJKLMNOPQRSTUV'
    return ''.join(
        [subst[int(binary[5 * i : 5 * i + 5], 2)] for i in range(length // 5)]
    )


if __name__ == '__main__':
    try:
        import qrcode
    except ImportError:
        raise SystemExit('Install \'qrcode\' module to run demo')

    code = generate(
        amount=1,
        iban='SK7700000000000000000000',
        swift='FIOZSKBAXXX',
        variable_symbol='11',
        constant_symbol='22',
        specific_symbol='33',
        beneficiary_name='Foo',
        beneficiary_address_1='address 1',
        beneficiary_address_2='address 2',
        note='bar',
    )
    print(code)
    img = qrcode.make(code)
    img.show()
