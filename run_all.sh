#/bin/sh

python run_analysis.py -H -S a -m -o -D ~/data/ampc24/analysis/arm/step_30 -R step 30
python run_analysis.py -H -S a -m -o -D ~/data/ampc24/analysis/arm/step_60 -R step 60
python run_analysis.py -H -S a -m -o -D ~/data/ampc24/analysis/arm/step_120 -R step 120
python run_analysis.py -H -S a -m -o -D ~/data/ampc24/analysis/arm/step_180 -R step 180
python run_analysis.py -H -S a -m -o -D ~/data/ampc24/analysis/arm/step_270 -R step 270

python run_analysis.py -H -S a -m -o -k -D ~/data/ampc24/analysis/arm/ramp_2pi_10 -R ramp 10
python run_analysis.py -H -S a -m -o -k -D ~/data/ampc24/analysis/arm/ramp_2pi_7.5 -R ramp 7.5
python run_analysis.py -H -S a -m -o -k -D ~/data/ampc24/analysis/arm/ramp_2pi_5 -R ramp 5
python run_analysis.py -H -S a -m -o -k -D ~/data/ampc24/analysis/arm/ramp_2pi_2.5 -R ramp 2.5

python run_analysis.py -H -S a -k -m -o -D ~/data/ampc24/analysis/arm/cos_60_2 -R cos 60 2
python run_analysis.py -H -S a -k -m -o -D ~/data/ampc24/analysis/arm/cos_60_3 -R cos 60 3
python run_analysis.py -H -S a -k -m -o -D ~/data/ampc24/analysis/arm/cos_60_4 -R cos 60 4

python run_analysis.py -H -S a -k -m -o -D ~/data/ampc24/analysis/arm/cos_90_2 -R cos 90 2
python run_analysis.py -H -S a -k -m -o -D ~/data/ampc24/analysis/arm/cos_90_3 -R cos 90 3
python run_analysis.py -H -S a -k -m -o -D ~/data/ampc24/analysis/arm/cos_90_4 -R cos 90 4



python run_analysis.py -H -S b -m -o -D ~/data/ampc24/analysis/beam/step_0.1 -R step 0.1
python run_analysis.py -H -S b -m -o -D ~/data/ampc24/analysis/beam/step_0.2 -R step 0.2
python run_analysis.py -H -S b -m -o -D ~/data/ampc24/analysis/beam/step_0.3 -R step 0.3
python run_analysis.py -H -S b -m -o -D ~/data/ampc24/analysis/beam/step_0.4 -R step 0.4

python run_analysis.py -H -S b -k -m -o -D ~/data/ampc24/analysis/beam/ramp_0.4 -R ramp 0.1

python run_analysis.py -H -S b -k -m -o -D ~/data/ampc24/analysis/beam/cos_0.2_1 -R cos 0.2 1
python run_analysis.py -H -S b -k -m -o -D ~/data/ampc24/analysis/beam/cos_0.2_2 -R cos 0.2 2
python run_analysis.py -H -S b -k -m -o -D ~/data/ampc24/analysis/beam/cos_0.2_3 -R cos 0.2 3
python run_analysis.py -H -S b -k -m -o -D ~/data/ampc24/analysis/beam/cos_0.2_4 -R cos 0.2 4
python run_analysis.py -H -S b -k -m -o -D ~/data/ampc24/analysis/beam/cos_0.2_5 -R cos 0.2 5



python run_analysis.py -H -S m -m -o -D ~/data/ampc24/analysis/multirotor/step_1_pi2 -R step 1 2
python run_analysis.py -H -S m -m -o -D ~/data/ampc24/analysis/multirotor/step_2_pi1.5 -R step 2 1.5
python run_analysis.py -H -S m -m -o -D ~/data/ampc24/analysis/multirotor/step_5_pi -R step 5 1
python run_analysis.py -H -S m -m -o -D ~/data/ampc24/analysis/multirotor/step_10_2pi -R step 10 0.5

python run_analysis.py -H -S m -m -o -D ~/data/ampc24/analysis/multirotor/step_1_pi2_q2 -Q 1 1 10 1 1 1 2 2 2 -R step 1 2
python run_analysis.py -H -S m -m -o -D ~/data/ampc24/analysis/multirotor/step_2_pi1.5_q2 -Q 1 1 10 1 1 1 2 2 2 -R step 2 1.5
python run_analysis.py -H -S m -m -o -D ~/data/ampc24/analysis/multirotor/step_5_pi_q2 -Q 1 1 10 1 1 1 2 2 2 -R step 5 1
python run_analysis.py -H -S m -m -o -D ~/data/ampc24/analysis/multirotor/step_10_2pi_q2 -Q 1 1 10 1 1 1 2 2 2 -R step 10 0.5

python run_analysis.py -H -S m -k -m -o -D ~/data/ampc24/analysis/multirotor/wavy_1_5_2_6 -R wavy 1 5 2 6
python run_analysis.py -H -S m -k -m -o -D ~/data/ampc24/analysis/multirotor/wavy_1_5_4_6 -R wavy 1 5 4 6
python run_analysis.py -H -S m -k -m -o -D ~/data/ampc24/analysis/multirotor/wavy_2_5_2_6 -R wavy 2 5 2 6
python run_analysis.py -H -S m -k -m -o -D ~/data/ampc24/analysis/multirotor/wavy_2_4_5_4 -R wavy 2 4 5 4

python run_analysis.py -H -S m -k -m -o -D ~/data/ampc24/analysis/multirotor/wavy_1_5_2_6_q2 -Q 1 1 10 1 1 1 2 2 2  -R wavy 1 5 2 6
python run_analysis.py -H -S m -k -m -o -D ~/data/ampc24/analysis/multirotor/wavy_1_5_4_6_q2 -Q 1 1 10 1 1 1 2 2 2  -R wavy 1 5 4 6
python run_analysis.py -H -S m -k -m -o -D ~/data/ampc24/analysis/multirotor/wavy_2_5_2_6_q2 -Q 1 1 10 1 1 1 2 2 2  -R wavy 2 5 2 6
python run_analysis.py -H -S m -k -m -o -D ~/data/ampc24/analysis/multirotor/wavy_2_4_5_4_q2 -Q 1 1 10 1 1 1 2 2 2  -R wavy 2 4 5 4

python run_analysis.py -H -S m -m -o -D ~/data/ampc24/analysis/multirotor/ramp1_5 -R ramp1 5
python run_analysis.py -H -S m -m -o -D ~/data/ampc24/analysis/multirotor/ramp1_10 -R ramp1 10
python run_analysis.py -H -S m -m -o -D ~/data/ampc24/analysis/multirotor/ramp1_15 -R ramp1 15
python run_analysis.py -H -S m -m -o -D ~/data/ampc24/analysis/multirotor/ramp1_20 -R ramp1 20
python run_analysis.py -H -S m -m -o -D ~/data/ampc24/analysis/multirotor/ramp1_25 -R ramp1 25

python run_analysis.py -H -S m -m -o -D ~/data/ampc24/analysis/multirotor/ramp3_5 -R ramp3 5
python run_analysis.py -H -S m -m -o -D ~/data/ampc24/analysis/multirotor/ramp3_6 -R ramp3 6
python run_analysis.py -H -S m -m -o -D ~/data/ampc24/analysis/multirotor/ramp3_7 -R ramp3 7
python run_analysis.py -H -S m -m -o -D ~/data/ampc24/analysis/multirotor/ramp3_8 -R ramp3 8
python run_analysis.py -H -S m -m -o -D ~/data/ampc24/analysis/multirotor/ramp3_9 -R ramp3 9
python run_analysis.py -H -S m -m -o -D ~/data/ampc24/analysis/multirotor/ramp3_10 -R ramp3 10
