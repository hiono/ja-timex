import re

from ja_timex.tag import TIMEX
from ja_timex.tagger.place import Pattern, Place, get_season_id, get_weekday_id


def parse_absdate(re_match: re.Match, pattern: Pattern) -> TIMEX:
    args = re_match.groupdict()
    span = re_match.span()

    # fill unknown position by "X"
    if "calendar_year" not in args:
        args["calendar_year"] = "XXXX"
    if "calendar_month" not in args:
        args["calendar_month"] = "XX"
    if "calendar_day" not in args:
        args["calendar_day"] = "XX"
    # zero padding
    args["calendar_year"] = args["calendar_year"].zfill(4)
    args["calendar_month"] = args["calendar_month"].zfill(2)
    args["calendar_day"] = args["calendar_day"].zfill(2)

    # additional_info = None
    # if "weekday" in args:
    #     additional_info = {"weekday_text": args["weekday"], "weekday_id": get_weekday_id(args["weekday"])}

    return TIMEX(
        type="DATE",
        value=f'{args["calendar_year"]}-{args["calendar_month"]}-{args["calendar_day"]}',
        value_from_surface=f'{args["calendar_year"]}-{args["calendar_month"]}-{args["calendar_day"]}',
        text=re_match.group(),
        value_format="absdate",
        parsed=args,
        span=span,
    )


def parse_weekday(re_match: re.Match, pattern: Pattern) -> TIMEX:
    args = re_match.groupdict()
    span = re_match.span()

    weekday_id = get_weekday_id(args["weekday"])
    calendar_week = "XX"
    value = f"XXXX-W{calendar_week}-{weekday_id}"
    return TIMEX(
        type="DATE",
        value=value,
        value_from_surface=value,
        text=re_match.group(),
        value_format="weekday",
        parsed=args,
        span=span,
    )


def parse_season(re_match: re.Match, pattern: Pattern) -> TIMEX:
    args = re_match.groupdict()
    span = re_match.span()

    season_id = get_season_id(args["season"])
    if "calendar_year" in args and args["calendar_year"]:
        year = args["calendar_year"].zfill(4)
    else:
        year = "XXXX"
    value = f"{year}-{season_id}"
    return TIMEX(
        type="DATE",
        value=value,
        value_from_surface=value,
        text=re_match.group(),
        value_format="season",
        parsed=args,
        span=span,
    )


def parse_quarter(re_match: re.Match, pattern: Pattern) -> TIMEX:
    args = re_match.groupdict()
    span = re_match.span()

    quarter_id = args["quarter"]
    value = f"XXXX-Q{quarter_id}"
    return TIMEX(
        type="DATE",
        value=value,
        value_from_surface=value,
        text=re_match.group(),
        value_format="quarter",
        parsed=args,
        span=span,
    )


def parse_fiscal_year(re_match: re.Match, pattern: Pattern) -> TIMEX:
    args = re_match.groupdict()
    span = re_match.span()

    fiscal_year = args["fiscal_year"]
    value = f"FY{fiscal_year}"
    return TIMEX(
        type="DATE",
        value=value,
        value_from_surface=value,
        text=re_match.group(),
        value_format="fiscal_year",
        parsed=args,
        span=span,
    )


def parse_ac_century(re_match: re.Match, pattern: Pattern) -> TIMEX:
    args = re_match.groupdict()
    span = re_match.span()

    century_num = int(args["ac_century"])
    century_range = f"{century_num - 1}" + "XX"
    value = century_range.zfill(4)
    return TIMEX(
        type="DATE",
        value=value,
        value_from_surface=value,
        text=re_match.group(),
        value_format="century",
        parsed=args,
        span=span,
    )


def parse_bc_year(re_match: re.Match, pattern: Pattern) -> TIMEX:
    args = re_match.groupdict()
    span = re_match.span()

    bc_year = args["bc_year"]
    value = f"BC{bc_year.zfill(4)}"
    return TIMEX(
        type="DATE",
        value=value,
        value_from_surface=value,
        text=re_match.group(),
        value_format="bc_year",
        parsed=args,
        span=span,
    )


def parse_bc_century(re_match: re.Match, pattern: Pattern) -> TIMEX:
    args = re_match.groupdict()
    span = re_match.span()

    century_num = int(args["bc_century"])
    century_range = f"{century_num - 1}" + "XX"
    value = "BC" + century_range.zfill(4)
    return TIMEX(
        type="DATE",
        value=value,
        value_from_surface=value,
        text=re_match.group(),
        value_format="bc_century",
        parsed=args,
        span=span,
    )


def parse_time(re_match: re.Match, pattern: Pattern) -> TIMEX:
    args = re_match.groupdict()
    span = re_match.span()

    # fill unknown position by "X"
    if "clock_hour" not in args:
        args["clock_hour"] = "XX"
    if "clock_minutes" not in args:
        args["clock_minutes"] = "XX"
    if "clock_second" not in args:
        args["clock_second"] = "XX"

    # zero padding
    hour = args["clock_hour"].zfill(2)
    minutes = args["clock_minutes"].zfill(2)
    second = args["clock_second"].zfill(2)

    # AM/PMを24時間表記に変更する
    if args.get("am_prefix") or args.get("am_suffix"):
        if hour == "12":
            hour = "00"
    if args.get("pm_prefix") or args.get("pm_suffix"):
        if hour != "XX" and 1 <= int(hour) <= 11:
            hour = str(int(hour) + 12)

    value = f"T{hour}-{minutes}-{second}"
    return TIMEX(
        type="TIME",
        value=value,
        value_from_surface=value,
        text=re_match.group(),
        value_format="time",
        parsed=args,
        span=span,
    )


p = Place()
patterns = []


# 日付
date_templates = [
    f"{p.calendar_year}年{p.calendar_month}月{p.calendar_day}日",
    f"{p.calendar_month}月{p.calendar_day}日",  # 年は表現できる範囲が広いため、年/月より月/日を優先する
    f"{p.calendar_year}年{p.calendar_month}月",
    f"{p.calendar_year}年",
    f"{p.calendar_month}月",
    f"{p.calendar_day}日",
]
for delimiter in ["/", "\\-", "\\.", "・", ","]:
    date_templates.append(f"{p.calendar_year}年?{delimiter}{p.calendar_month}月?{delimiter}{p.calendar_day}日?")
    date_templates.append(f"{p.calendar_month}月?{delimiter}{p.calendar_day}日?")
    date_templates.append(f"{p.calendar_year}年?{delimiter}{p.calendar_month}月?")

for date_template in date_templates:
    patterns.append(
        Pattern(
            re_pattern=date_template,
            parse_func=parse_absdate,
            option={},
        )
    )


# 曜日
patterns += [
    Pattern(
        re_pattern=p.weekday_with_symbol,
        parse_func=parse_weekday,
        option={},
    ),
    Pattern(
        re_pattern=f"({p.calendar_year}[年|/]?)?{p.season}",
        parse_func=parse_season,
        option={},
    ),
    Pattern(
        re_pattern=f"(第{p.quarter}四半期)",
        parse_func=parse_quarter,
        option={},
    ),
    Pattern(
        re_pattern=f"(Q{p.quarter})",
        parse_func=parse_quarter,
        option={},
    ),
    Pattern(
        re_pattern=f"({p.quarter}Q)",
        parse_func=parse_quarter,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.fiscal_year}年度",
        parse_func=parse_fiscal_year,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.ac_century}世紀",
        parse_func=parse_ac_century,
        option={},
    ),
    Pattern(
        re_pattern=f"紀元前{p.bc_year}年",
        parse_func=parse_bc_year,
        option={},
    ),
    Pattern(
        re_pattern=f"紀元前{p.bc_century}世紀",
        parse_func=parse_bc_century,
        option={},
    ),
]

# 時刻
patterns += [
    Pattern(
        re_pattern=f"{p.ampm_prefix}?{p.clock_hour}時{p.clock_minutes}分{p.clock_second}秒",
        parse_func=parse_time,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.ampm_prefix}?{p.clock_hour}時{p.clock_minutes}分{p.ampm_suffix}?",
        parse_func=parse_time,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.clock_minutes}分{p.clock_second}秒",
        parse_func=parse_time,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.ampm_prefix}?{p.clock_hour}時{p.ampm_suffix}?",
        parse_func=parse_time,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.clock_minutes}分",
        parse_func=parse_time,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.clock_second}秒",
        parse_func=parse_time,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.ampm_prefix}?{p.clock_hour}:{p.clock_minutes}:{p.clock_second}{p.ampm_suffix}?",
        parse_func=parse_time,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.ampm_prefix}?{p.clock_hour}:{p.clock_minutes}{p.ampm_suffix}?",
        parse_func=parse_time,
        option={},
    ),
    Pattern(
        re_pattern=f"{p.clock_minutes}:{p.clock_second}",
        parse_func=parse_time,
        option={},
    ),
]
