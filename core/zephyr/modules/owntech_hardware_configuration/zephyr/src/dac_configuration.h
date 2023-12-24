/*
 * Copyright (c) 2023 LAAS-CNRS
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU Lesser General Public License as published by
 *   the Free Software Foundation, either version 2.1 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU Lesser General Public License for more details.
 *
 *   You should have received a copy of the GNU Lesser General Public License
 *   along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 * SPDX-License-Identifier: LGLPV2.1
 */

/**
 * @date   2023
 * @author Clément Foucher <clement.foucher@laas.fr>
 * @author Luiz Villa <luiz.villa@laas.fr>
 * @author Ayoub Farah Hassan <ayoub.farah-hassan@laas.fr>
 */


#ifndef DAC_CONFIGURATION_H_
#define DAC_CONFIGURATION_H_

// Stdlib
#include <stdint.h>

//ARM_MATH
#include <arm_math.h>

// hrtim.h is important to configure the DAC for current mode
#include "hrtim.h"


void dac_config_const_value_init(uint8_t dac_number);
void dac_set_const_value(uint8_t dac_number, uint8_t channel, uint32_t const_value);
void dac_config_dac3_current_mode_init(hrtim_tu_t tu_src);
void dac_config_dac1_current_mode_init(hrtim_tu_t tu_src);
void set_satwtooth_DAC3(float32_t set_voltage, float32_t reset_voltage);
void set_satwtooth_DAC1(float32_t set_voltage, float32_t reset_voltage);

#endif // DAC_CONFIGURATION_H_
