# Визуализатор Git
Создает граф коммитов на базе библиотеки **graphviz**.
## Использование
Для запуска программы вводится команда:
* Для Windows:
```
python main.py [.git path]
python main.py "/project/.git/" # example
```
* Для Linux:
```
python3 main.py [.git path]
python3 main.py "/project/.git/" # example
```
## Результат работы
Программа создает изображение графа в формате PDF или GV. В графе содержится описание хэшей коммитов и их описаний, имена веток и файлов, измененные или добавленные файлы между коммитами.   

Пример:  
![image](https://github.com/user-attachments/assets/1f0882d2-b57e-4223-8433-14fdc2afb78a)
