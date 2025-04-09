#!/bin/sh

data_dir=~/data/ampc_case_studies
run="python run_analysis.py -H -m -o -S"
run_arm=1
run_beam=1
run_cart=1
run_pendulum=1
run_multirotor=1

## Arm
if [ $run_arm -eq 1 ]; then
    sys=arm
    ref=step
    for amp in 30 60 120 180 270
    do
        echo "$run $sys -D $data_dir/$sys/${ref}_${amp} -R $ref $amp"
        $run $sys -D $data_dir/$sys/${ref}_${amp} -R $ref $amp
    done

    ref=ramp
    for scale in 2.5 5 7.5 10
    do
        echo "$run $sys -k -D $data_dir/$sys/${ref}_2pi_$scale -R $ref $scale"
        $run $sys -k -D $data_dir/$sys/${ref}_2pi_$scale -R $ref $scale
    done

    ref=cos
    for amp in 60 90
    do
        for periods in 2 3 4
        do
            echo "$run $sys -k -D $data_dir/$sys/${ref}_${amp}_$periods -R $ref $amp $periods"
            $run $sys -k -D $data_dir/$sys/${ref}_${amp}_$periods -R $ref $amp $periods
        done
    done
fi


## Cart Pendulum (controlling cart)
if [ $run_cart -eq 1 ]; then
    sys=cart
    ref=step
    for amp in 1 2 5 10
    do
        echo "$run $sys -D $data_dir/$sys/${ref}_$amp -R $ref $amp"
        $run $sys -D $data_dir/$sys/${ref}_$amp -R $ref $amp
    done

    ref=cos
    for amp in 2 5
    do
        for periods in 1 2 3 4
        do
            echo "$run $sys -k -D $data_dir/$sys/${ref}_${amp}_$periods -R $ref $amp $periods"
            $run $sys -k -D $data_dir/$sys/${ref}_${amp}_$periods -R $ref $amp $periods
        done
    done

    ref=ramp
    for amp in 2 3 4 5
    do
        echo "$run $sys -k -D $data_dir/$sys/${ref}_$amp -R $ref $amp"
        $run $sys -k -D $data_dir/$sys/${ref}_$amp -R $ref $amp
    done


## Cart Pendulum (controlling pendulum)
if [ $run_pendulum -eq 1 ]; then
    sys=pendulum
    ref=step
    for amp in 5 15 30 45
    do
        echo "$run $sys -D $data_dir/$sys/${ref}_$amp -R $ref $amp"
        $run $sys -D $data_dir/$sys/${ref}_$amp -R $ref $amp
    done

    ref=cos
    for amp in 15 25
    do
        for periods in 1 2 3 4
        do
            echo "$run $sys -k -D $data_dir/$sys/${ref}_${amp}_$periods -R $ref $amp $periods"
            $run $sys -k -D $data_dir/$sys/${ref}_${amp}_$periods -R $ref $amp $periods
        done
    done

    ref=ramp
    for amp in 5 15 30 45
    do
        echo "$run $sys -k -D $data_dir/$sys/${ref}_$amp -R $ref $amp"
        $run $sys -k -D $data_dir/$sys/${ref}_$amp -R $ref $amp
    done
fi


## Block Beam
if [ $run_beam -eq 1 ]; then
    sys=beam
    ref=step
    for amp in 0.1 0.2 0.3 0.4
    do
        echo "$run $sys -D $data_dir/$sys/${ref}_$amp -R $ref $amp"
        $run $sys -D $data_dir/$sys/${ref}_$amp -R $ref $amp
    done

    ref=ramp
    for d in 0.2 0.3 0.4
    do
        echo "$run $sys -k -D $data_dir/$sys/${ref}_$d -R $ref $d"
        $run $sys -k -D $data_dir/$sys/${ref}_$d -R $ref $d
    done

    ref=cos
    for amp in 0.2
    do
        for periods in 1 2 3 4 5
        do
            echo "$run $sys -k -D $data_dir/$sys/${ref}_${amp}_$periods -R $ref $amp $periods"
            $run $sys -k -D $data_dir/$sys/${ref}_${amp}_$periods -R $ref $amp $periods
        done
    done
fi


## Multirotor
if [ $run_multirotor -eq 1 ]; then
    sys=multirotor
    ref=step
    for amp in 1,2 2,1.5 5,1 10,0.5
    do
        IFS=',' read pos yaw << EOF
$amp
EOF
        echo "$run $sys -D $data_dir/$sys/${ref}_${pos}_pi$yaw -R $ref $pos $yaw"
        $run $sys -D $data_dir/$sys/${ref}_${pos}_pi$yaw -R $ref $pos $yaw

        echo "$run $sys -D $data_dir/$sys/${ref}_${pos}_pi${yaw}_q2 -Q 1 1 10 1 1 1 2 2 2 -R $ref $pos $yaw"
        $run $sys -D $data_dir/$sys/${ref}_${pos}_pi${yaw}_q2 -Q 1 1 10 1 1 1 2 2 2 -R $ref $pos $yaw
    done

    ref=wavy
    for params in 1,5,2,6 1,5,4,6 2,5,2,6 2,4,5,4
    do
        IFS=',' read amp1 amp2 amp3 amp4 << EOF
$params
EOF
        echo "$run $sys -k -D $data_dir/$sys/${ref}_${amp1}_${amp2}_${amp3}_$amp4 -R $ref $amp1 $amp2 $amp3 $amp4"
        $run $sys -k -D $data_dir/$sys/${ref}_${amp1}_${amp2}_${amp3}_$amp4 -R $ref $amp1 $amp2 $amp3 $amp4

        echo "$run $sys -k -D $data_dir/$sys/${ref}_${amp1}_${amp2}_${amp3}_${amp4}_q2 -Q 1 1 10 1 1 1 2 2 2 -R $ref $amp1 $amp2 $amp3 $amp4"
        $run $sys -k -D $data_dir/$sys/${ref}_${amp1}_${amp2}_${amp3}_${amp4}_q2 -Q 1 1 10 1 1 1 2 2 2 -R $ref $amp1 $amp2 $amp3 $amp4
    done

    ref=ramp1
    for amp in 5 10 15 20 25
    do
        echo "$run $sys -D $data_dir/$sys/${ref}_$amp -R $ref $amp"
        $run $sys -D $data_dir/$sys/${ref}_$amp -R $ref $amp
    done

    ref=ramp3
    for amp in 5 6 7 8 9 10
    do
        echo "$run $sys -D $data_dir/$sys/${ref}_$amp -R $ref $amp"
        $run $sys -D $data_dir/$sys/${ref}_$amp -R $ref $amp
    done
fi
