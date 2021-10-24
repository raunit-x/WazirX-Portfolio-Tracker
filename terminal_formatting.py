from sty import fg, ef, rs
from token_constants import *


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def progress_bar(index, total, bar_len=50):
    percent_done = (index + 1) / total * 100
    percent_done = round(percent_done, 1)

    done = round(percent_done / (100 / bar_len))
    togo = bar_len - done

    done_str = '█' * int(done)
    togo_str = '░' * int(togo)

    print(f'{BColors.WARNING if percent_done < 100 else BColors.OKCYAN}GATHERING DATA: [{done_str}{togo_str}] '
          f'{percent_done}% Done{BColors.ENDC}', end='\r')


color_encoding = [fg.li_cyan, (fg.li_red, fg.da_green), fg.cyan, fg.yellow, (fg.li_red, fg.da_green),
                  (fg.li_red, fg.da_green)]
text_formatting = [ef.bold, rs.dim_bold, ef.bold, rs.dim_bold, ef.bold, ef.bold]
prefixes = ['', RUPEE, '', RUPEE, RUPEE, (UP_ARROW, DOWN_ARROW)]
