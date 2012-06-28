source_host=sourcehost
source_user=user
source_pass=pass
source_db=dbname

dest_host=desthost
dest_user=user
dest_pass=pass
dest_db=dbname

ignore=( \
	'ignore_table_1' \
	'ignore_table_2' \
	'ignore_table_3' \
)

tmp_path="/tmp/"
tmp_filename="${source_db}_$(date +"%Y-%m-%d").sql"
tmp_file=$tmp_path$tmp_filename

echo "Проверяем, есть ли свеженький дамп (${tmp_file})."

if [ -f $tmp_file ]; then
	echo "Дамп нашёлся, используем его"
elif [ ! -w $tmp_path ]; then
	echo "Ошибка. Временная директория недоступна для записи (${tmp_path})."
	exit 1
else
	echo "Дамп не найден. Загружаем с сервера ${source_host}."

	dump_cmd="mysqldump -h${source_host} -u${source_user} -p${source_pass} ${source_db}."

	ignore_length=${#ignore[@]}
	for (( i=0;i<ignore_length;i++)); do
		dump_cmd=${dump_cmd}" --ignore_table=${source_db}.${ignore[${i}]}"
	done

	dump_cmd="${dump_cmd} > ${tmp_file}"

	eval $dump_cmd

	echo "Дамп сохранён в файл ${tmp_file}."
fi

echo "Раскатываем дамп на ${dest_host}."

mysql -h${dest_host} -u${dest_user} -p${dest_pass} ${dest_db} < ${tmp_file}

echo "Готово."

