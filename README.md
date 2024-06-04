# PAY by square

Generate codes for [by square](https://bysquare.com/) payments.

## Installation

Note: `pay-by-square` generates a string that can be passed to a QR code generator to create
an image. To run the example below, you need to install the
[qrcode module](https://github.com/lincolnloop/python-qrcode) as well.

```sh
pip install pay-by-square
```

## Usage

### API

```text
pay_by_square.generate(
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
    Generate pay-by-square code that can be used to create a QR code for banking apps

    If the date is not provided, the current date will be used.

    The 'iban' parameter can be provided in the following formats:
    1. A single string representing an IBAN.
    2. A list of strings, each representing an IBAN.
    3. A list of lists, where each sublist contains an IBAN and an optional SWIFT code.

    Note: If you provide the 'iban' parameter as a list, the SWIFT codes will be handled
    separately from the 'swift' parameter, which will then be ignored.
    The maximum number of IBANs allowed is 5.
```

### Example 1

```python
import qrcode
import pay_by_square


code = pay_by_square.generate(
    amount=10,
    iban='SK7283300000009111111118',
    swift='FIOZSKBAXXX',
    variable_symbol='47',
)

print(code)
img = qrcode.make(code)
img.show()
```

### Example 2

```python
import qrcode
import pay_by_square


code = pay_by_square.generate(
    amount=10,
    iban=['SK7283300000009111111118', 'SK7283300000009111111119'],
    variable_symbol='47',
)

print(code)
img = qrcode.make(code)
img.show()
```

### Example 3

```python
import qrcode
import pay_by_square


code = pay_by_square.generate(
    amount=10,
    iban=[
        ['SK7283300000009111111118', 'FIOZSKBAXXX'],
        ['SK7283300000009111111119']
    ],
    variable_symbol='47',
)

print(code)
img = qrcode.make(code)
img.show()
```

## Testing

```sh
python -m unittest tests.py
```

---

Kudos to [guys from devel.cz](https://devel.cz/otazka/qr-kod-pay-by-square)
