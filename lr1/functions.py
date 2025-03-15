def convert_number_to_binary_code(x):
    if x > 127 or x < -127:
        print("Number can not be more than 127 and less than -127")
        exit(0)
    if x < 0:
        y = abs(x)
        binary_number = '1'
    else:
        y = x
        binary_number = '0'
    binary_part = ''
    if y == 0:
        binary_part = '0'
    else:
        while y > 0:
            binary_part = str(y % 2) + binary_part
            y //= 2
    while len(binary_part) < 7:
        binary_part = '0' + binary_part
    return binary_number + binary_part

def get_revers_code(binary_number):
    if binary_number[0] == '0':
        return binary_number
    reverse_binary_number = binary_number[0]
    for i in range(len(binary_number)):
        if i == 0: continue
        if binary_number[i] == '1':
            reverse_binary_number += '0'
        elif binary_number[i] == '0':
            reverse_binary_number += '1'
        else: continue
    return reverse_binary_number

def get_additional_code(reverse_binary_number):
    if reverse_binary_number[0] == '0':
        return reverse_binary_number
    additional_code = ''
    number_to_add = 1
    if reverse_binary_number[0] == '0':
        return reverse_binary_number
    for i in reversed(reverse_binary_number):
        if i == '1' and number_to_add == 1:
            additional_code += '0'
        elif i == '0' and number_to_add == 1:
            additional_code += '1'
            number_to_add = 0
        else:
            additional_code += i
    if number_to_add == 1:
        additional_code += '1'
    return additional_code[::-1]


def binary_to_signed_decimal(binary_str, is_twos_complement=True):
    if binary_str[0] == '1':
        if is_twos_complement:
            inverted = ''.join('1' if bit == '0' else '0' for bit in binary_str)
            carry = 1
            additional = ''
            for bit in reversed(inverted):
                if bit == '1' and carry == 1:
                    additional = '0' + additional
                elif bit == '0' and carry == 1:
                    additional = '1' + additional
                    carry = 0
                else:
                    additional = bit + additional
            decimal_value = 0
            for i, bit in enumerate(reversed(additional)):
                decimal_value += int(bit) * (2 ** i)
            decimal_value = -decimal_value
        else:

            decimal_value = 0
            for i, bit in enumerate(reversed(binary_str[1:])):
                decimal_value += int(bit) * (2 ** i)
            decimal_value = -decimal_value
    else:

        decimal_value = 0
        for i, bit in enumerate(reversed(binary_str)):
            decimal_value += int(bit) * (2 ** i)
    return decimal_value
def binary_data(x):
    print(x)
    x = convert_number_to_binary_code(x)
    print(x)
    x = get_revers_code(x)
    print(x)
    x = get_additional_code(x)
    print(x)
def binary_addition(a, b):
    if a > 0:
        bin1 = convert_number_to_binary_code(a)
    elif a < 0:
        bin1 = get_additional_code(get_revers_code(convert_number_to_binary_code(a)))
    else:
        bin1 = convert_number_to_binary_code(0)  # Если a = 0

    if b > 0:
        bin2 = convert_number_to_binary_code(b)
    elif b < 0:
        bin2 = get_additional_code(get_revers_code(convert_number_to_binary_code(b)))
    else:
        bin2 = convert_number_to_binary_code(0)  # Если b = 0

    carry = 0
    result = ''

    for i in range(7, -1, -1):
        total = int(bin1[i]) + int(bin2[i]) + carry
        result = str(total % 2) + result
        carry = total // 2

    sign1 = bin1[0]
    sign2 = bin2[0]
    sign_res = result[0]

    if sign1 == sign2 and sign1 != sign_res:
        print("Переполнение!")
        result = result[1:]
    result_decimal = binary_to_signed_decimal(result)
    print("result: ")
    binary_data(result_decimal)
    return result_decimal
def binary_subtraction(a, b):
    b = -b
    return binary_addition(a, b)
def binary_multiplication(a, b):
    bin1 = convert_number_to_binary_code(a)
    bin2 = convert_number_to_binary_code(b)
    if len(bin1) != 8 or len(bin2) != 8:
        raise ValueError("Оба бинарных числа должны быть 8-битными строками.")
    sign_res = '0' if (bin1[0] == bin2[0]) else '1'

    bin1 = bin1[1:]
    bin2 = bin2[1:]

    result = '00000000'
    for i in range(7):
        if bin2[6 - i] == '1':
            shifted_bin1 = bin1 + '0' * i
            result = binary_addition_binary_strings(result, shifted_bin1)


    result = sign_res + result[-7:]

    return result

def binary_addition_binary_strings(bin1, bin2):
    max_len = max(len(bin1), len(bin2))
    bin1 = bin1.zfill(max_len)
    bin2 = bin2.zfill(max_len)

    carry = '0'
    result = ''
    for i in range(max_len - 1, -1, -1):
        total = int(bin1[i]) + int(bin2[i]) + int(carry)
        result = str(total % 2) + result
        carry = str(total // 2)

    return result

def subtract_binary(bin1, bin2):

    bin1 = bin1.zfill(8)[-8:]
    bin2 = bin2.zfill(8)[-8:]


    inverted_bin2 = ''.join('1' if bit == '0' else '0' for bit in bin2)
    carry = 1
    additional_bin2 = ''
    for bit in reversed(inverted_bin2):
        if bit == '1' and carry == 1:
            additional_bin2 = '0' + additional_bin2
        elif bit == '0' and carry == 1:
            additional_bin2 = '1' + additional_bin2
            carry = 0
        else:
            additional_bin2 = bit + additional_bin2

    result = ''
    carry = 0
    for i in range(7, -1, -1):
        sum_bits = int(bin1[i]) + int(additional_bin2[i]) + carry
        result = str(sum_bits % 2) + result
        carry = sum_bits // 2

    result = result[-8:]

    return result

def binary_division(dividend, divisor):

    sign_dividend = '1' if dividend < 0 else '0'
    sign_divisor = '1' if divisor < 0 else '0'
    result_sign = '1' if sign_dividend != sign_divisor else '0'

    dividend_abs = abs(dividend)
    divisor_abs = abs(divisor)

    bin_dividend = convert_number_to_binary_code(dividend_abs)
    bin_divisor = convert_number_to_binary_code(divisor_abs)

    result = ''
    remainder = 0

    for i in range(8):
        remainder = (remainder << 1) | int(bin_dividend[i])
        if remainder >= divisor_abs:
            result += '1'
            remainder -= divisor_abs
        else:
            result += '0'
    result = result_sign + result[-7:]

    result += '.'

    for _ in range(5):
        remainder <<= 1

        if remainder >= divisor_abs:
            result += '1'
            remainder -= divisor_abs
        else:
            result += '0'

    return result
def binary_fixed_point_to_decimal(binary_str):
    if '.' in binary_str:
        integer_part, fractional_part = binary_str.split('.')
    else:
        integer_part, fractional_part = binary_str, ''

    sign = -1 if integer_part[0] == '1' else 1
    integer_part = integer_part[1:]

    decimal_integer = 0
    for i, bit in enumerate(reversed(integer_part)):
        decimal_integer += int(bit) * (2 ** i)


    decimal_fraction = 0
    for i, bit in enumerate(fractional_part):
        decimal_fraction += int(bit) * (2 ** -(i + 1))


    return sign * (decimal_integer + decimal_fraction)
def float_to_ieee754(num):
    result = [0]
    bits_for_mantissa = 23
    integer_part = int(num)
    fractional_part = num - integer_part

    binary = []
    if integer_part == 0:
        binary = ['0']
    while integer_part > 0:
        binary.insert(0, str(integer_part % 2))
        integer_part //= 2

    binary.append('.')
    for _ in range(bits_for_mantissa):
        fractional_part *= 2
        bit = int(fractional_part)
        binary.append(str(bit))
        fractional_part -= bit

    binary_str = ''.join(binary)
    point_pos = binary_str.index('.')
    first_one_pos = binary_str.replace('.', '').index('1')

    exponent = point_pos - first_one_pos - 1 + 127

    for i in range(7, -1, -1):
        result.append(1 if exponent & (1 << i) else 0)


    mantissa_start = first_one_pos + 1
    mantissa = binary_str.replace('.', '')[mantissa_start:mantissa_start + bits_for_mantissa]
    mantissa = mantissa.ljust(bits_for_mantissa, '0')
    result.extend([int(x) for x in mantissa])

    return result
def ieee754_to_float(ieee):
    shift = 127
    bits_for_exp = 8
    bits_for_mantissa = 23
    sign = ieee[0]
    exponent = 0
    for i in range(1, bits_for_exp + 1):
        exponent = exponent * 2 + ieee[i]
    exponent -= shift

    mantissa = 1.0
    for i in range(bits_for_exp + 1, bits_for_exp + bits_for_mantissa + 1):
        mantissa += ieee[i] * (2 ** -(i - 8))


    value = mantissa * (2 ** exponent)
    return -value if sign else value

def addition_float(first, second):
    first_ieee = float_to_ieee754(first)
    second_ieee = float_to_ieee754(second)
    print(first_ieee)
    print(second_ieee)
    first_float = ieee754_to_float(first_ieee)
    second_float = ieee754_to_float(second_ieee)
    print(first_float)
    print(second_float)
    result = first_float + second_float

    return result










