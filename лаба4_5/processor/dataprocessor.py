from abc import ABC, abstractmethod     # подключаем инструменты для создания абстрактных классов
import pandas       # пакет для работы с датасетами
import numpy as np

"""
    В данном модуле реализуются классы обработчиков для 
    применения алгоритма обработки к различным типам файлов (csv или txt).
    
    ВАЖНО! Если реализация различных обработчиков занимает большое 
    количество строк, то необходимо оформлять каждый класс в отдельном файле
"""


class DataProcessor(ABC):
    """ Родительский класс для обработчиков файлов """

    def __init__(self, datasource):
        # общие атрибуты для классов обработчиков данных
        self._datasource = datasource   # путь к источнику данных
        self._dataset = None            # входной набор данных
        self.result = None              # выходной набор данных (результат обработки)

    # Все методы, помеченные декоратором @abstractmethod, ОБЯЗАТЕЛЬНЫ для переобределения
    @abstractmethod
    def read(self) -> bool:
        """ Метод, инициализирующий источник данных """
        pass

    @abstractmethod
    def run(self) -> None:
        """ Точка запуска методов обработки данных """
        pass

    """
        Метод sort_data_by_col - пример одного из методов обработки данных.
        В данном случае метод просто сортирует входной датасет по наименованию 
        заданной колонки (аргумент colname) и устанвливает тип сортировки: 
        ascending = True - по возрастанию, ascending = False - по убыванию
        
        ВАЖНО! Следует логически разделять методы обработки, например, отдельный метод для сортировки, 
        отдельный метод для удаления "пустот" в датасете (очистка) и т.д. Это позволит гибко применять необходимые
        методы при переопределении метода run для того или иного типа обработчика.
        НАПРИМЕР, если ваш источник данных это не файл, а база данных, тогда метод сортировки будет не нужен,
        т.к. сортировку можно сделать при выполнении SQL-запроса типа SELECT ... ORDER BY...
    """

    def sort_data_by_col(self, df: pandas.DataFrame, colname: str, asc: bool) -> pandas.DataFrame:
        return df.sort_values(by=[colname], ascending=asc)

    """
        Метод get_mean_value_by_filter выбирает из входного набора данных строки с заданным условием 
        (фильтр), используя инструкцию DataFrame.query(), применяет к получившимся значением функцию 
        mean (считает среднее значения в колонках) и возвращает результат в виде нового DataFrame.
        
        Подробнее по фильтрации строк с помощью query() см.: https://sparkbyexamples.com/pandas/pandas-filter-by-column-value/
    """
    def get_mean_value_by_filter(self, df: pandas.DataFrame, filter_expr: str) -> pandas.DataFrame:
        result = df.query(filter_expr)
        return result.mean(axis=0, skipna=True).to_frame().T


    @abstractmethod
    def print_result(self) -> None:
        """ Абстрактный метод для вывода результата на экран """
        pass


class CsvDataProcessor(DataProcessor):
    """ Реализация класса-обработчика csv-файлов """

    def __init__(self, datasource):
        # Переопределяем конструктор родительского класса
        DataProcessor.__init__(self, datasource)    # инициализируем конструктор родительского класса для получения общих атрибутов
        self.separators = [';', ',', '|']        # список допустимых разделителей

    """
        Переопределяем метод инициализации источника данных.
        Т.к. данный класс предназначен для чтения CSV-файлов, то используем метод read_csv
        из библиотеки pandas
    """
    def read(self):
        try:
            # Пытаемся преобразовать данные файла в pandas.DataFrame, используя различные разделители
            for separator in self.separators:
                self._dataset = pandas.read_csv(self._datasource, sep=separator, header='infer', names=None, encoding="utf-8")
                # Читаем имена колонок из файла данных
                col_names = self._dataset.columns
                # Если количество считанных колонок > 1 возвращаем True
                if len(col_names) > 1:
                    print(f'Columns read: {col_names} using separator {separator}')
                    return True
        except Exception as e:
            print(e)
        return False

    def run(self):
        # Сортируем данные по значениям колонки "LKG" и сохраняем результат в атрибуте result
        self.result = pandas.DataFrame()
        #target_values = [1, 2, 3]       # значения колонки "target" для фильтрации
        #for t in target_values:
            # фильтруем строки по каждому возможному значению колонки "target" и вычисляем среднее
            #result = self.get_mean_value_by_filter(self._dataset, f"target == {t}")
            # полученный результат (DataFrame) на каждой итерации добавляем в результирующий DataFrame в self.result
            #self.result = pandas.concat([self.result, result], ignore_index=True)
         # удаляем выбросы
        col_namess = self._dataset.columns
        for i in range(len(col_namess)):
            self._dataset [col_namess[i]].replace('', np.nan, inplace=True)
            self._dataset.dropna(subset=[col_namess[i]], inplace=True)

        # создаем колонку для разбития на категории
        self._dataset ["price_category"] = pandas.cut(self._dataset["selling_price"],[0,500000,1500000,np.inf], labels = [1,2,3])
        self.result = self.sort_data_by_col(self._dataset, "selling_price", True)

    def print_result(self):
        print(f'Running CSV-file processor!\n', self.result)


class TxtDataProcessor(DataProcessor):
    """ Реализация класса-обработчика txt-файлов """

    def read(self):
        """ Реализация метода для чтения TXT-файла (разедитель колонок - пробелы) """
        try:
            self._dataset = pandas.read_table(self._datasource, sep='\s+', engine='python')
            col_names = self._dataset.columns
            if len(col_names) < 2:
                return False
            return True
        except Exception as e:
            print(str(e))
            return False

    def run(self):
        #self.result = self.sort_data_by_col(self._dataset, "LKG", True)
        self.result = self.sort_data_by_col(self._dataset, "selling_price", True)

    def print_result(self):
        print(f'Running TXT-file processor!\n', self.result)
