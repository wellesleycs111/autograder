#!/bin/bash

for student in ashen rkim8 myang5 kchen7 ssong3 hmurayam aklufas mshen2 cverish vzhang3 osalomon mvohra yzhang16 eduncan2 evanlaar ychi2 skim62 lfutami kgao jsarmien mwu4 hweissma mokoli rpak npirani hcantuol dfeinsch cchen15 aleon mshum2 kcox3 sma4 mmuldown acao klin3 amynick cdigenna epostel skerwin cmarti10 ihenders tli2 dharsono cwhitak4 cblazey rkobayas istaccun bquader khuertas jaguilar crubera rhu2 cdesai hvenkata avalle jstryker jwu12 tbakshi hscheide moh2 yakhavan gpovedas jzhang5 sjoshipu lwang3 abenjam2 mkelley2 mkim14 elee10 mjarami2 cadupoku; do
    mkdir Desktop/spring16ps/$student/autograder/;
    mkdir Desktop/spring16ps/$student/psetsolutions/;
    mv Desktop/spring16ps/$student/*.py Desktop/spring16ps/$student/psetsolutions/;
    cp -r autograder/ Desktop/spring16ps/$student/autograder/ ;
    cd Desktop/spring16ps/$student/autograder/;
    python autograder.py;
    cd ../../../../
done
