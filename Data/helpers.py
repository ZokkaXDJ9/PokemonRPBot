import random

CRIT = 6
FAIL_THRESHOLD = 3

class ParsedRollQuery:
    def __init__(self, amount: int = 1, sides: int = 6, flat_addition: int = 0):
        self.amount = max(1, min(amount, 100))
        self.sides = max(2, min(sides, 100))
        self.flat_addition = flat_addition

    @classmethod
    def from_query(cls, query: str):
        """Parse a query like '1d6+5'."""
        flat_addition = 0
        if '+' in query:
            query, add_value = query.split('+', 1)
            flat_addition = int(add_value)

        if 'd' in query:
            amount_str, sides_str = query.split('d', 1)
            amount = int(amount_str) if amount_str else 1
            sides = int(sides_str) if sides_str else 6
        else:
            amount = int(query)
            sides = 6

        return cls(amount, sides, flat_addition)

    def as_button_callback_query_string(self) -> str:
        return f"roll-dice_{self.amount}d{self.sides}+{self.flat_addition}"

    def execute(self) -> str:
        results = []
        total = self.flat_addition
        six_count = 0
        successes = 0

        for _ in range(self.amount):
            value = random.randint(1, self.sides)
            total += value
            if value > FAIL_THRESHOLD:
                successes += 1
                if value == CRIT:
                    six_count += 1
            results.append(value)

        result_list = ", ".join(
            f"**__{x}__**" if x == CRIT else f"**{x}**" if x > FAIL_THRESHOLD else str(x)
            for x in results
        )

        text = f"{self.amount}d{self.sides}"
        if self.flat_addition > 0:
            text += f" + {self.flat_addition} — {result_list} + {self.flat_addition} = {total}"
        else:
            text += f" — {result_list}"

        if self.sides == 6:
            success_string = "Successes." if successes != 1 else "Success."
            crit_string = " **(CRIT)**" if six_count >= 3 else ""
            text += f"\n**{successes}** {success_string}{crit_string}"

        return text
