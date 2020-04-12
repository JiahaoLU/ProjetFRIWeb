# encoding: utf-8
"""
@author: Jiahao LU
@contact: lujiahao8146@gmail.com
@file: ResultAccuracy.py
@time: 2020/4/4
@desc: The function to check result accuracy comparing with corrected query output.
"""
from typing import Tuple


def calculate_result_accuracy(correction: str, result: str) -> Tuple[float, int, int]:
    correctdir = './Queries/dev_output/' + correction
    resdir = '../results/' + result
    with open(correctdir, 'r') as corrector:
        correct_ans = set([line for line in corrector])
        with open(resdir, 'r') as answers:
            ans = set([line for line in answers])
            bingo = len(ans.intersection(correct_ans))
            cnt = len(ans)
    return (bingo, cnt, len(correct_ans)) if cnt != 0 else (0.0, 0, len(correct_ans))


if __name__ == '__main__':
    cor, ans_num, total = calculate_result_accuracy('7.out', 'vectorial.thethe19.06.40.out')
    R = cor / total
    P = cor / ans_num
    f1 = 2 * P * R / (P + R)
    print(cor, ans_num, total, cor/total)
    print('f1 = ', f1)