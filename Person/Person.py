import numpy


class Person:
    def __init__(self, gender: str, weight: int, drinking_period: float, drink_type):
        self.gender = gender
        self.weight = weight
        self.drinking_period = drinking_period
        self.drink_type = drink_type
        self.effect_levels = [0.060, 0.099]

    @staticmethod
    def recalculate_standard_drink(drink, part=1.0):
        drinks_dict = {
            'beer': {
                'agrams': 13 * part,
                'avg_drink_period': 0.5
            }
        }
        return drinks_dict[drink]

    @staticmethod
    def calculate_alc_loss(break_time: float):
        return (0.02 / 60) * break_time

    def ebac(self, drink,  recalculated_drink_period=0):
        body_water_in_blood = 0.806
        body_water = 0.58 if self.gender == 'male' else 0.49
        metabolism_const = 0.015 if self.gender == 'male' else 0.017

        drink_period = recalculated_drink_period if recalculated_drink_period != 0 else drink['avg_drink_period']

        ebac = ((body_water_in_blood * (drink['agrams'] / 10) * 1.2)
                / (body_water * self.weight)) - metabolism_const * drink_period

        return round(ebac, 5)

    def execute_drinking(self, break_time, level, drink_part):
        ebac_total = 0
        time_total = 0
        drinking_plan = []
        while ebac_total <= level:
            drink = self.recalculate_standard_drink(self.drink_type, drink_part)
            next_ebac_level = ebac_total + self.ebac(drink)

            if next_ebac_level <= level:
                drinking_plan.append('drink_{}_{}'.format(self.drink_type, drink_part))
                time_total += drink['avg_drink_period']
                ebac_total += next_ebac_level
            elif next_ebac_level > level:
                drinking_plan.append('drink_{}_{}'.format(self.drink_type, drink_part / 2))
                drink = self.recalculate_standard_drink(self.drink_type, drink_part / 2)
                time_total += drink['avg_drink_period']
                ebac_total += self.ebac(drink)

            drinking_plan.append('break_{}'.format(break_time))
            ebac_total -= self.calculate_alc_loss(break_time)
            time_total += break_time / 60

            if ebac_total < 0:
                break

        ebac_total = round(ebac_total, 3)

        takes_enough_time = time_total <= self.drinking_period
        gives_enough_ebac = self.effect_levels[0] <= ebac_total <= self.effect_levels[-1]
        return {'ebac': ebac_total, 'is_success': takes_enough_time and gives_enough_ebac, 'drinking_plan': drinking_plan}

    def optimize_with_break_time(self, break_time, levels):
        output = []
        current_level = 0
        while break_time > 0:
            current = self.execute_drinking(break_time, levels[current_level], 1)
            is_success = current['is_success']

            if is_success:
                output.append(current)

            if current_level == len(levels) - 1:
                current_level = 0
                break_time -= 1
            else:
                current_level += 1

        return output

    def optimize_with_drink_part(self, break_time, levels, step):
        drink_part = 1
        output = []
        current_level = 0
        while drink_part >= 0.15:
            current = self.execute_drinking(break_time, levels[current_level], drink_part)
            is_success = current['is_success']
            if is_success:
                output.append(current)

            if current_level == len(levels) - 1:
                current_level = 0
                drink_part = round(drink_part - step, 2)
            else:
                current_level += 1

        return output

    def start_calculating(self, start_break_time, drink_part_dec_step, levels=[]):
        default_levels = [
            self.effect_levels[0],
            numpy.mean(self.effect_levels),
            self.effect_levels[-1]
        ]
        given_levels = default_levels if not len(levels) else levels

        breaks_output = self.optimize_with_break_time(start_break_time, given_levels)
        drink_part_output = self.optimize_with_drink_part(start_break_time, given_levels, drink_part_dec_step)

        return {
            'breaks_output': breaks_output,
            'drink_part_output': drink_part_output
        }


