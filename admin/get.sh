./getResults.sh |tee results.log
count=0;
echo
echo overall summary : 
for cat in `cat category.list`
do  
    count=$[count+1]
    line1=`cat results.log|grep completed|head -n $count|tail -n 1`
    line2=`cat results.log|grep time|head -n $count|tail -n 1`
    echo $line1 - $cat
    echo $line2
done