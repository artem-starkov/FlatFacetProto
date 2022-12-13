import math
from app.utils.enums import TestCases


class Generator:
    def __init__(self, g):
        self._g = g
        self._h = 50
        self._l = 25
        self._rMax = 1000

    def get_dataset_for_validating(self, m, test_case):
        dataset = []
        if test_case == TestCases.ROUND_CASE:
            for radius in range(200, 901, 100):
                dataset += self._generate(m, 1000, test_case, {'radius': radius})
        elif test_case == TestCases.HORIZONTAL_CASE:
            for k in range(200, 901, 100):
                dataset += self._generate(m, 1000, test_case, {'k': k})
        else:
            for angle in range(81, 99, 1):
                dataset += self._generate(m, 1000, test_case, {'alpha_in_degrees': angle, 'x_start': 1})
        return dataset

    @staticmethod
    def get_blue_zone_dataset(dataset, m, left_from=318, left_to=400, right_from=338, right_to=420):
        d = list()
        center = int(m / 2)
        for i in range(0, len(dataset)):
            precedent = dataset[i]
            left_eye = precedent[:center]
            left_eye_seen = left_eye[center - (center - left_from):center - (center - left_to)]
            right_eye = precedent[center:m]
            right_eye_seen = right_eye[center - (center - right_from):center - (center - right_to)]
            if sum(left_eye_seen) > 0 and sum(right_eye_seen) > 0:
                d.append(precedent)
        # print(len(d), '/', len(dataset))
        return d

    @staticmethod
    def transform_to_small_dataset(dataset, m, left_from=318, left_to=400, right_from=338, right_to=420):
        d = list()
        center = int(m / 2)
        for i in range(0, len(dataset)):
            precedent = dataset[i]
            left_eye = precedent[:center]
            left_eye_seen = left_eye[center - (center - left_from):center - (center - left_to)]
            right_eye = precedent[center:m]
            right_eye_seen = right_eye[center - (center - right_from):center - (center - right_to)]
            d.append(list(left_eye_seen) + list(right_eye_seen) + [precedent[m], precedent[m + 1]])
        return d

    def _generate(self, m, n, test_case, values, gap=1, rMin=50):
        psi = math.asin(self._l / self._h)
        M = []
        for precedents in range(n):
            if test_case == TestCases.ROUND_CASE:
                r, fi, can_continue = self._generate_round_case(psi, values['radius'], precedents, gap)
                if not can_continue:
                    break
            elif test_case == TestCases.HORIZONTAL_CASE:
                r, fi, can_continue = self._generate_horizontal_case(values['k'], precedents, gap)
                if not can_continue:
                    break
            elif test_case == TestCases.LINE_CASE:
                r, fi, can_continue = self._generate_line_case(self._rMax, values['x_start'], values['alpha_in_degrees'],
                                                               precedents, gap)
                if not can_continue:
                    break
            else:
                r, fi, can_continue = self._generate_vertical_case(values['rMax'], precedents, gap, rMin)
                if not can_continue:
                    break
            if fi < psi + math.asin(self._g / r) or fi > math.pi - psi - math.asin(self._g / r):
                continue
            r_b = math.sqrt(self._h * self._h + r * r - 2 * self._h * r * math.cos(fi))
            if self._g > r_b:
                continue
            fi_b = math.pi - math.acos(
                (self._h - r * math.cos(fi)) / math.sqrt(self._h * self._h + r * r - 2 * self._h * r * math.cos(fi)))
            L_b = math.floor((m / (2 * math.pi)) * (fi_b - math.asin(self._g / r_b)))
            R_b = math.floor((m / (2 * math.pi)) * (fi_b + math.asin(self._g / r_b)))
            r_a = math.sqrt(self._h * self._h + r * r + 2 * self._h * r * math.cos(fi))
            if self._g > r_a:
                continue
            fi_a = math.acos(
                (self._h + r * math.cos(fi)) / math.sqrt(self._h * self._h + r * r + 2 * self._h * r * math.cos(fi)))
            L_a = math.floor((m / (2 * math.pi)) * (fi_a - math.asin(self._g / r_a)))
            R_a = math.floor((m / (2 * math.pi)) * (fi_a + math.asin(self._g / r_a)))
            if L_a < 0:
                continue
            if R_b >= m // 2:
                continue
            beta_A = [0] * (m // 2)
            beta_B = [0] * (m // 2)
            for j in range(L_a, R_a + 1):
                beta_A[j] = 1
            for j in range(L_b, R_b + 1):
                beta_B[j] = 1
            M.append(beta_A + beta_B + [r, fi, self._g, r * math.cos(fi), r * math.sin(fi), self._h, self._l])
        return M

    def _generate_round_case(self, psi, radius, i, gap):
        r = radius
        fi0 = psi + math.asin(self._g / r) + 0.001
        dfi = math.acos((2 * r * r - 4 * self._g * self._g * gap * gap) / (2 * r * r))
        fi = fi0 + i * dfi
        if fi > math.pi - psi - math.asin((self._g * gap) / r):
            return r, fi, False
        return r, fi, True

    def _generate_vertical_case(self, rMax, i, gap, rMin=50):
        fi = math.pi / 2
        r = rMin + i * 2 * self._g * gap
        can_continue = r <= rMax
        return r, fi, can_continue

    def _generate_horizontal_case(self, k, i, gap):
        r0 = 2 * k
        x0 = r0 * math.cos(math.asin(k / r0))
        x = x0 - 2 * i * self._g * gap
        r = math.sqrt(x * x + k * k)
        if x < 0:
            fi = math.pi - math.asin(k / r)
        else:
            fi = math.asin(k / r)
        can_continue = x > -r0
        return r, fi, can_continue

    def _generate_line_case(self, rMax, x, alpha_in_degrees, i, gap):
        x = abs(x)
        alpha = math.radians(alpha_in_degrees)
        r = math.sqrt(x * x + 4 * i * i * self._g * self._g * gap * gap - 4 * self._g * gap * i * x * math.cos(alpha))
        dfi = math.asin((2 * self._g * gap * i * math.sin(alpha)) / r)
        if x - i * 2 * self._g * gap * math.cos(alpha) > 0:
            fi = math.pi - dfi
        else:
            fi = dfi
        can_continue = r <= rMax
        if r < 50:
            return rMax * 2, fi, can_continue
        return r, fi, can_continue
