dumbase
=======

Загружает дамп базы данных с боевого сервера и раскатывает его на среде разработки.


Возможности
-----------

* Исключение таблиц (например, логов), перечисленных в массиве `$ignore`.
* Повторное использование дампа, загруженного в тот же день.


Использование
-------------

1. Загрузить скрипт (`git clone`).
1. Установить права на выполнение (`chmod +x dumbase.sh`).
1. Отредактировать скрипт, указав параметры баз данных (`$source_*`, `$dest_*`)
и путь для сохранения временных файлов (`$tmp_path`).
1. Запустить скрипт (`./dumbase.sh`)


Тудушечка
---------

1. Вынести конфиги (или, ещё кошернее, использовать предустановленные конфиги проектов).
1. Добавить возможность указывать регулярку для исключения таблиц из дампа.
1. Добавить параметр "порт", ибо не портом 3306 единым.
1. Изменить механизм кэширования дампов (отсчитывать время от момента создания файла,
добавить возможность контролировать время кэширования, добавить флаг
для принудительного обновления дампа)

