from sty import fg, bg, ef, rs


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


# print(f"{fg.li_green}Warning: No active formats remain. Continue?{rs.inverse}")
# print(f"{BColors.OKCYAN}{ef.inverse} This is bold text {ef.italic} This is italic text{rs.inverse}")
