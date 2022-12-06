# Set text colours
RED='\033[0;31m'
GREEN='\033[0;32m'
ENDCOLOUR='\033[0m'


# Run eventlog file
python3 eventlog.py 

if [ $? -ne 0 ]
then
    echo -e "$RED Test failed$ENDCOLOUR"
    exit 1
else 
    if [ -s "eventlog.csv" ]
    then
        echo -e "$GREEN File sucessfully created$ENDCOLOUR"
        exit 0
    else 
        echo -e "$RED File empty$ENDCOLOUR"
        exit 1
    fi

fi

if [ -f "eventlog.csv" ]
then
    rm eventlog.csv
fi