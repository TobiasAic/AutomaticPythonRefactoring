from textwrap import dedent

"""
These refactoring suggestions are a selection from Martin Fowler's Refactoring Catalog (https://refactoring.com/catalog/ as of 29.08.2026).
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
        if (anEmployee.seniority < 2) return 0;
        if (anEmployee.monthsDisabled > 12) return 0;
        if (anEmployee.isPartTime) return 0;
    """).strip()

    example_after = dedent("""
        if (isNotEligibleForDisability()) return 0;

        function isNotEligibleForDisability() {
            return ((anEmployee.seniority < 2)
                    || (anEmployee.monthsDisabled > 12)
                    || (anEmployee.isPartTime));
        }
    """).strip()

    notes = dedent("""""").strip()


class DecomposeConditional(RefactoringSuggestion):
    name = "Decompose Conditional"

    example_before = dedent("""
        if (!aDate.isBefore(plan.summerStart) && !aDate.isAfter(plan.summerEnd))
            charge = quantity * plan.summerRate;
        else
            charge = quantity * plan.regularRate + plan.regularServiceCharge; 
    """).strip()

    example_after = dedent("""
        if (summer())
            charge = summerCharge();
        else
            charge = regularCharge(); 
    """).strip()

    notes = dedent("""""").strip()

class ExtractClass(RefactoringSuggestion):
    name = "Extract Class"

    example_before = dedent("""
       class Person {
            get officeAreaCode() {return this._officeAreaCode;}
            get officeNumber()   {return this._officeNumber;} 
        } 
    """).strip()

    example_after = dedent("""
        class Person {
            get officeAreaCode() {return this._telephoneNumber.areaCode;}
            get officeNumber()   {return this._telephoneNumber.number;}
        }
        class TelephoneNumber {
            get areaCode() {return this._areaCode;}
            get number()   {return this._number;}
        }  
    """).strip()

    notes = dedent("""
        Make sure to not change the public API of the original class.
    """).strip()

class ExtractFunction(RefactoringSuggestion):
    name = "Extract Function"

    example_before = dedent("""
        function printOwing(invoice) {
            printBanner();
            let outstanding  = calculateOutstanding();

            //print details
            console.log(`name: ${invoice.customer}`);
            console.log(`amount: ${outstanding}`);  
        } 
    """).strip()

    example_after = dedent("""
        function printOwing(invoice) {
            printBanner();
            let outstanding = calculateOutstanding();
            printDetails(outstanding);

            function printDetails(outstanding) {
                console.log(`name: ${invoice.customer}`);
                console.log(`amount: ${outstanding}`);
            }
        } 
    """).strip()

    notes = dedent("""
        Use the provided tool.
    """).strip()

class ExtractVariable(RefactoringSuggestion):
    name = "Extract Variable"

    example_before = dedent("""
        return order.quantity * order.itemPrice -
            Math.max(0, order.quantity - 500) * order.itemPrice * 0.05 +
            Math.min(order.quantity * order.itemPrice * 0.1, 100); 
    """).strip()

    example_after = dedent("""
        const basePrice = order.quantity * order.itemPrice;
        const quantityDiscount = Math.max(0, order.quantity - 500) * order.itemPrice * 0.05;
        const shipping = Math.min(basePrice * 0.1, 100);
        return basePrice - quantityDiscount + shipping; 
    """).strip()

    notes = dedent("""""").strip()


class InlineClass(RefactoringSuggestion):
    name = "Inline Class"

    example_before = dedent("""
        class Person {
            get officeAreaCode() {return this._telephoneNumber.areaCode;}
            get officeNumber()   {return this._telephoneNumber.number;}
        }
        class TelephoneNumber {
            get areaCode() {return this._areaCode;}
            get number()   {return this._number;}
        } 
    """).strip()

    example_after = dedent("""
        class Person {
            get officeAreaCode() {return this._officeAreaCode;}
            get officeNumber()   {return this._officeNumber;} 
        }
    """).strip()

    notes = dedent("""
        Make sure to not change the public API of the original class.
    """).strip()


class InlineFunction(RefactoringSuggestion):
    name = "Inline Function"

    example_before = dedent("""
        function getRating(driver) {
            return moreThanFiveLateDeliveries(driver) ? 2 : 1;
        }

        function moreThanFiveLateDeliveries(driver) {
            return driver.numberOfLateDeliveries > 5;
        } 
    """).strip()

    example_after = dedent("""
        function getRating(driver) {
            return (driver.numberOfLateDeliveries > 5) ? 2 : 1;
        }  
    """).strip()

    notes = dedent("""""").strip()

class InlineVariable(RefactoringSuggestion):
    name = "Inline Variable"

    example_before = dedent("""
        let basePrice = anOrder.basePrice;
        return (basePrice > 1000); 
    """).strip()

    example_after = dedent("""
        return anOrder.basePrice > 1000; 
    """).strip()

    notes = dedent("""""").strip()

class PreserveWholeObject(RefactoringSuggestion):
    name = "Preserve Whole Object"

    example_before = dedent("""
        const low = aRoom.daysTempRange.low;
        const high = aRoom.daysTempRange.high;
        if (aPlan.withinRange(low, high)) 
    """).strip()

    example_after = dedent("""
       if (aPlan.withinRange(aRoom.daysTempRange)) 
    """).strip()

    notes = dedent("""
        Make sure to not change the public API of the class or function.
    """).strip()

class RemoveDeadCode(RefactoringSuggestion):
    name = "Remove Dead Code"

    example_before = dedent("""
        if(false) {
            doSomethingThatUsedToMatter();
        } 
    """).strip()

    example_after = dedent("""
        
    """).strip()

    notes = dedent("""""").strip()

class RenameVariable(RefactoringSuggestion):
    name = "Rename Variable"

    example_before = dedent("""
       let a = height * width; 
    """).strip()

    example_after = dedent("""
       let area = height * width; 
    """).strip()

    notes = dedent("""
        Use the provided tool.
    """).strip()

class ReplaceControlFlagWithBreak(RefactoringSuggestion):
    name = "Replace Control Flag with Break"

    example_before = dedent("""
        for (const p of people) {
            if (! found) {
                if ( p === “Don”) {
                    sendAlert();
                    found = true;
                }
            }
        } 
    """).strip()

    example_after = dedent("""
        for (const p of people) {
            if ( p === “Don”) {
                sendAlert();
                break;
            }
        }
    """).strip()

    notes = dedent("""""").strip()

class ReplaceExceptionWithPrecheck(RefactoringSuggestion):
    name = "Replace Exception with Precheck"

    example_before = dedent("""
        double getValueForPeriod (int periodNumber) {
            try {
                return values[periodNumber];
            } catch (ArrayIndexOutOfBoundsException e) {
                return 0;
            }
        } 
    """).strip()

    example_after = dedent("""
        double getValueForPeriod (int periodNumber) {
            return (periodNumber >= values.length) ? 0 : values[periodNumber];
        } 
    """).strip()

    notes = dedent("""
        Make sure to not change the behavior of the function.
        If it raised an exception before, it should still raise an exception.
    """).strip()

class ReplaceLoopWithPipeline(RefactoringSuggestion):
    name = "Replace Loop with Pipeline"

    example_before = dedent("""
        const names = [];
        for (const i of input) {
            if (i.job === “programmer”)
            names.push(i.name);
        }
    """).strip()

    example_after = dedent("""
        const names = input
            .filter(i => i.job === “programmer”)
            .map(i => i.name)
        ; 
    """).strip()

    notes = dedent("""""").strip()


class ReplaceMagicLiteral(RefactoringSuggestion):
    name = "Replace Magic Literal"

    example_before = dedent("""
        function potentialEnergy(mass, height) {
            return mass * 9.81 * height;
        } 
    """).strip()

    example_after = dedent("""
        const STANDARD_GRAVITY = 9.81;
        function potentialEnergy(mass, height) {
            return mass * STANDARD_GRAVITY * height;
        } 
    """).strip()

    notes = dedent("""""").strip()


class ReplaceNestedConditionalWithGuardClauses(RefactoringSuggestion):
    name = "Replace Nested Conditional with Guard Clauses"

    example_before = dedent("""
        function getPayAmount() {
            let result;
            if (isDead)
                result = deadAmount();
            else {
                if (isSeparated)
                    result = separatedAmount();
                else {
                    if (isRetired)
                        result = retiredAmount();
                    else
                        result = normalPayAmount();
                }
            }
            return result;
        }
    """).strip()

    example_after = dedent("""
        function getPayAmount() {
            if (isDead) return deadAmount();
            if (isSeparated) return separatedAmount();
            if (isRetired) return retiredAmount();
            return normalPayAmount();
        } 
    """).strip()

    notes = dedent("""""").strip()


class ReplaceTempWithQuery(RefactoringSuggestion):
    name = "Replace Temp with Query"

    example_before = dedent("""
        const basePrice = this._quantity * this._itemPrice;
        if (basePrice > 1000)
            return basePrice * 0.95;
        else
            return basePrice * 0.98; 
    """).strip()

    example_after = dedent("""
        get basePrice() {this._quantity * this._itemPrice;}
            
        ...
            
        if (this.basePrice > 1000)
            return this.basePrice * 0.95;
        else
            return this.basePrice * 0.98; 
    """).strip()

    notes = dedent("""""").strip()


class SlideStatements(RefactoringSuggestion):
    name = "Slide Statements"

    example_before = dedent("""
        const pricingPlan = retrievePricingPlan();
        const order = retrieveOrder();
        let charge;
        const chargePerUnit = pricingPlan.unit; 
    """).strip()

    example_after = dedent("""
        const pricingPlan = retrievePricingPlan();
        const chargePerUnit = pricingPlan.unit;
        const order = retrieveOrder();
        let charge;
    """).strip()

    notes = dedent("""""").strip()


class SplitLoop(RefactoringSuggestion):
    name = "Split Loop"

    example_before = dedent("""
        let averageAge = 0;
        let totalSalary = 0;
        for (const p of people) {
            averageAge += p.age;
            totalSalary += p.salary;
        }
        averageAge = averageAge / people.length; 
    """).strip()

    example_after = dedent("""
        let totalSalary = 0;
        for (const p of people) {
            totalSalary += p.salary;
        }

        let averageAge = 0;
        for (const p of people) {
            averageAge += p.age;
        }
        averageAge = averageAge / people.length;
    """).strip()

    notes = dedent("""""").strip()


class SplitVariable(RefactoringSuggestion):
    name = "Split Variable"

    example_before = dedent("""
       let temp = 2 * (height + width);
        console.log(temp);
        temp = height * width;
        console.log(temp);
    """).strip()

    example_after = dedent("""
        const perimeter = 2 * (height + width);
        console.log(perimeter);
        const area = height * width;
        console.log(area);
    """).strip()

    notes = dedent("""""").strip()


class SubstituteAlgorithm(RefactoringSuggestion):
    name = "Substitute Algorithm"

    example_before = dedent("""
        function foundPerson(people) {
            for(let i = 0; i < people.length; i++) {
                if (people[i] === “Don”) {
                    return “Don”;
                }
                if (people[i] === “John”) {
                    return “John”;
                }
                if (people[i] === “Kent”) {
                    return “Kent”;
                }
            }
            return “”;
        } 
    """).strip()

    example_after = dedent("""
        function foundPerson(people) {
            const candidates = [”Don”, “John”, “Kent”];
            return people.find(p => candidates.includes(p)) || '';
        }
    """).strip()

    notes = dedent("""
        Do not do this for complex algorithms.
        A complex, specific algorithm is probably intended and should not change.
        Your job is not to improve performance.
    """).strip()