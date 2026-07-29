from textwrap import dedent

"""
These refactoring suggestions are a selection from Martin Fowler's Refactoring Catalog (https://refactoring.com/catalog/ as of 29.08.2026).
The examples were translated from JavaScript to Python.
"""


class RefactoringSuggestion:
    name = ""
    example_before = ""
    example_after = ""
    notes = ""

    @classmethod
    def get_description(cls) -> str:
        return dedent(f"""
            {cls.name}

            Example before:
            {cls.example_before}

            Example after:
            {cls.example_after}

            Notes:
            {cls.notes}
        """).strip()


class ConsolidateConditionalExpression(RefactoringSuggestion):
    name = "Consolidate Conditional Expression"

    example_before = dedent("""
        if anEmployee.seniority < 2:
            return 0
        if anEmployee.monthsDisabled > 12:
            return 0
        if anEmployee.isPartTime:
            return 0
    """).strip()

    example_after = dedent("""
        if is_not_eligible_for_disability():
            return 0

        def is_not_eligible_for_disability():
            return ((anEmployee.seniority < 2)
                    or (anEmployee.monthsDisabled > 12)
                    or (anEmployee.isPartTime))
    """).strip()

    notes = dedent("""""").strip()


class DecomposeConditional(RefactoringSuggestion):
    name = "Decompose Conditional"

    example_before = dedent("""
        if not aDate.isBefore(plan.summerStart) and not aDate.isAfter(plan.summerEnd):
            charge = quantity * plan.summerRate
        else:
            charge = quantity * plan.regularRate + plan.regularServiceCharge
    """).strip()

    example_after = dedent("""
        if summer():
            charge = summer_charge()
        else:
            charge = regular_charge()
    """).strip()

    notes = dedent("""""").strip()


class ExtractClass(RefactoringSuggestion):
    name = "Extract Class"

    example_before = dedent("""
        class Person:
            @property
            def officeAreaCode(self):
                return self._officeAreaCode

            @property
            def officeNumber(self):
                return self._officeNumber
    """).strip()

    example_after = dedent("""
        class Person:
            @property
            def officeAreaCode(self):
                return self._telephoneNumber.areaCode

            @property
            def officeNumber(self):
                return self._telephoneNumber.number

        class TelephoneNumber:
            @property
            def areaCode(self):
                return self._areaCode

            @property
            def number(self):
                return self._number
    """).strip()

    notes = dedent("""
        Make sure to not change the public API of the original class.
    """).strip()


class ExtractFunction(RefactoringSuggestion):
    name = "Extract Function"

    example_before = dedent("""
        def print_owing(invoice):
            print_banner()
            outstanding = calculate_outstanding()

            # print details
            print(f"name: {invoice.customer}")
            print(f"amount: {outstanding}")
    """).strip()

    example_after = dedent("""
        def print_owing(invoice):
            print_banner()
            outstanding = calculate_outstanding()
            print_details(outstanding)

            def print_details(outstanding):
                print(f"name: {invoice.customer}")
                print(f"amount: {outstanding}")
    """).strip()

    notes = dedent("""
        Use the provided tool.
    """).strip()


class ExtractVariable(RefactoringSuggestion):
    name = "Extract Variable"

    example_before = dedent("""
        return order.quantity * order.itemPrice -
            max(0, order.quantity - 500) * order.itemPrice * 0.05 +
            min(order.quantity * order.itemPrice * 0.1, 100)
    """).strip()

    example_after = dedent("""
        base_price = order.quantity * order.itemPrice
        quantity_discount = max(0, order.quantity - 500) * order.itemPrice * 0.05
        shipping = min(base_price * 0.1, 100)
        return base_price - quantity_discount + shipping
    """).strip()

    notes = dedent("""""").strip()


class InlineClass(RefactoringSuggestion):
    name = "Inline Class"

    example_before = dedent("""
        class Person:
            @property
            def officeAreaCode(self):
                return self._telephoneNumber.areaCode

            @property
            def officeNumber(self):
                return self._telephoneNumber.number

        class TelephoneNumber:
            @property
            def areaCode(self):
                return self._areaCode

            @property
            def number(self):
                return self._number
    """).strip()

    example_after = dedent("""
        class Person:
            @property
            def officeAreaCode(self):
                return self._officeAreaCode

            @property
            def officeNumber(self):
                return self._officeNumber
    """).strip()

    notes = dedent("""
        Make sure to not change the public API of the original class.
    """).strip()


class InlineFunction(RefactoringSuggestion):
    name = "Inline Function"

    example_before = dedent("""
        def get_rating(driver):
            return 2 if more_than_five_late_deliveries(driver) else 1

        def more_than_five_late_deliveries(driver):
            return driver.numberOfLateDeliveries > 5
    """).strip()

    example_after = dedent("""
        def get_rating(driver):
            return 2 if driver.numberOfLateDeliveries > 5 else 1
    """).strip()

    notes = dedent("""""").strip()


class InlineVariable(RefactoringSuggestion):
    name = "Inline Variable"

    example_before = dedent("""
        base_price = anOrder.basePrice
        return base_price > 1000
    """).strip()

    example_after = dedent("""
        return anOrder.basePrice > 1000
    """).strip()

    notes = dedent("""""").strip()


class PreserveWholeObject(RefactoringSuggestion):
    name = "Preserve Whole Object"

    example_before = dedent("""
        low = aRoom.daysTempRange.low
        high = aRoom.daysTempRange.high
        if aPlan.withinRange(low, high):
            pass
    """).strip()

    example_after = dedent("""
        if aPlan.withinRange(aRoom.daysTempRange):
            pass
    """).strip()

    notes = dedent("""
        Make sure to not change the public API of the class or function.
    """).strip()


class RemoveDeadCode(RefactoringSuggestion):
    name = "Remove Dead Code"

    example_before = dedent("""
        if False:
            do_something_that_used_to_matter()
    """).strip()

    example_after = dedent("""

    """).strip()

    notes = dedent("""""").strip()


class RenameVariable(RefactoringSuggestion):
    name = "Rename Variable"

    example_before = dedent("""
        a = height * width
    """).strip()

    example_after = dedent("""
        area = height * width
    """).strip()

    notes = dedent("""
        Use the provided tool.
    """).strip()


class ReplaceControlFlagWithBreak(RefactoringSuggestion):
    name = "Replace Control Flag with Break"

    example_before = dedent("""
        found = False
        for p in people:
            if not found:
                if p == "Don":
                    send_alert()
                    found = True
    """).strip()

    example_after = dedent("""
        for p in people:
            if p == "Don":
                send_alert()
                break
    """).strip()

    notes = dedent("""""").strip()


class ReplaceExceptionWithPrecheck(RefactoringSuggestion):
    name = "Replace Exception with Precheck"

    example_before = dedent("""
        def get_value_for_period(period_number):
            try:
                return values[period_number]
            except IndexError as e:
                return 0
    """).strip()

    example_after = dedent("""
        def get_value_for_period(period_number):
            return 0 if period_number >= len(values) else values[period_number]
    """).strip()

    notes = dedent("""
        Make sure to not change the behavior of the function.
        If it raised an exception before, it should still raise an exception.
    """).strip()


class ReplaceLoopWithPipeline(RefactoringSuggestion):
    name = "Replace Loop with Pipeline"

    example_before = dedent("""
        names = []
        for i in input:
            if i.job == "programmer":
                names.append(i.name)
    """).strip()

    example_after = dedent("""
        names = [i.name for i in input if i.job == "programmer"]
    """).strip()

    notes = dedent("""""").strip()


class ReplaceMagicLiteral(RefactoringSuggestion):
    name = "Replace Magic Literal"

    example_before = dedent("""
        def potential_energy(mass, height):
            return mass * 9.81 * height
    """).strip()

    example_after = dedent("""
        STANDARD_GRAVITY = 9.81

        def potential_energy(mass, height):
            return mass * STANDARD_GRAVITY * height
    """).strip()

    notes = dedent("""""").strip()


class ReplaceNestedConditionalWithGuardClauses(RefactoringSuggestion):
    name = "Replace Nested Conditional with Guard Clauses"

    example_before = dedent("""
        def get_pay_amount():
            result = None
            if is_dead:
                result = dead_amount()
            else:
                if is_separated:
                    result = separated_amount()
                else:
                    if is_retired:
                        result = retired_amount()
                    else:
                        result = normal_pay_amount()
            return result
    """).strip()

    example_after = dedent("""
        def get_pay_amount():
            if is_dead:
                return dead_amount()
            if is_separated:
                return separated_amount()
            if is_retired:
                return retired_amount()
            return normal_pay_amount()
    """).strip()

    notes = dedent("""""").strip()


class ReplaceTempWithQuery(RefactoringSuggestion):
    name = "Replace Temp with Query"

    example_before = dedent("""
        base_price = self._quantity * self._itemPrice
        if base_price > 1000:
            return base_price * 0.95
        else:
            return base_price * 0.98
    """).strip()

    example_after = dedent("""
        @property
        def basePrice(self):
            return self._quantity * self._itemPrice

        ...

        if self.basePrice > 1000:
            return self.basePrice * 0.95
        else:
            return self.basePrice * 0.98
    """).strip()

    notes = dedent("""""").strip()


class SlideStatements(RefactoringSuggestion):
    name = "Slide Statements"

    example_before = dedent("""
        pricingPlan = retrievePricingPlan()
        order = retrieveOrder()
        charge = None
        chargePerUnit = pricingPlan.unit
    """).strip()

    example_after = dedent("""
        pricingPlan = retrievePricingPlan()
        chargePerUnit = pricingPlan.unit
        order = retrieveOrder()
        charge = None
    """).strip()

    notes = dedent("""""").strip()


class SplitLoop(RefactoringSuggestion):
    name = "Split Loop"

    example_before = dedent("""
        averageAge = 0
        totalSalary = 0
        for p in people:
            averageAge += p.age
            totalSalary += p.salary
        averageAge = averageAge / len(people)
    """).strip()

    example_after = dedent("""
        totalSalary = 0
        for p in people:
            totalSalary += p.salary

        averageAge = 0
        for p in people:
            averageAge += p.age
        averageAge = averageAge / len(people)
    """).strip()

    notes = dedent("""""").strip()


class SplitVariable(RefactoringSuggestion):
    name = "Split Variable"

    example_before = dedent("""
        temp = 2 * (height + width)
        print(temp)
        temp = height * width
        print(temp)
    """).strip()

    example_after = dedent("""
        perimeter = 2 * (height + width)
        print(perimeter)
        area = height * width
        print(area)
    """).strip()

    notes = dedent("""""").strip()


class SubstituteAlgorithm(RefactoringSuggestion):
    name = "Substitute Algorithm"

    example_before = dedent("""
        def foundPerson(people):
            for i in range(len(people)):
                if people[i] == "Don":
                    return "Don"
                if people[i] == "John":
                    return "John"
                if people[i] == "Kent":
                    return "Kent"
            return ""
    """).strip()

    example_after = dedent("""
        def foundPerson(people):
            candidates = ["Don", "John", "Kent"]
            return next((p for p in people if p in candidates), '')
    """).strip()

    notes = dedent("""
        Do not do this for complex algorithms.
        A complex, specific algorithm is probably intended and should not change.
        Your job is not to improve performance.
    """).strip()