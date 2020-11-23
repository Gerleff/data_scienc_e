import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import warnings;

warnings.filterwarnings(action='once')

large = 22;
med = 16;
small = 12
params = {'axes.titlesize': large,
          'legend.fontsize': med,
          'figure.figsize': (16, 10),
          'axes.labelsize': med,
          'axes.titlesize': med,
          'xtick.labelsize': med,
          'ytick.labelsize': med,
          'figure.titlesize': large}
plt.rcParams.update(params)
plt.style.use('seaborn-whitegrid')
sns.set_style("white")
# %matplotlib inline

# Version
print(mpl.__version__)  # > 3.0.0
print(sns.__version__)  # > 0.9.0

DATA_FILE_PATH = 'data_set_Vic.dta'
CSV_FILE_PATH = 'data_set_Vic.csv'

if __name__ == '__main__':
    # data = pd.read_stata(DATA_FILE_PATH, convert_categoricals=False)
    # data.to_csv('data_set_Vic.csv', index=False)
    data = pd.read_csv(CSV_FILE_PATH, index_col=False)
    df = pd.DataFrame.from_records(data)
    base = df[['um1', 'um2', 'uj10', 'u_age', 'uh5', 'status', 'psu']]
    base = base[(base.um1 < 99999997.0) &
                (base.um2 < 99999997.0) &
                (base.uj10 < 99999997.0) &
                (base.u_age >= 19) &
                (base.u_age <= 72)]
    base['ИМТ'] = base.um1 / (base.um2 * base.um2 / 10000)
    base['Логарифм'] = np.log(base.uj10)
    base.columns = ['Вес', 'Рост', 'З/п', 'Возраст', 'Пол', 'Тип насел пункта', 'Номер региона', 'ИМТ', 'Логарифм з/п']

    male = base[['Пол', 'ИМТ']][base.Пол == 1]
    fem = base[['Пол', 'ИМТ']][base.Пол == 2]


    def int_info(base):
        return pd.DataFrame({
            'Соответствие между массой человека и его ростом': [
                'Выраженный дефицит массы тела',
                'Недостаточная (дефицит) масса тела',
                'Норма',
                'Избыточная масса тела (предожирение)',
                'Ожирение',
                'Ожирение резкое',
                'Очень резкое ожирение'
            ],
            'Количество пипл': [
                base['ИМТ'][base['ИМТ'] < 16.0].count(),
                base['ИМТ'][(base['ИМТ'] < 18.5) & (base['ИМТ'] >= 16.0)].count(),
                base['ИМТ'][(base['ИМТ'] < 25.0) & (base['ИМТ'] >= 18.5)].count(),
                base['ИМТ'][(base['ИМТ'] < 30.0) & (base['ИМТ'] >= 25.0)].count(),
                base['ИМТ'][(base['ИМТ'] < 35.0) & (base['ИМТ'] >= 30.0)].count(),
                base['ИМТ'][(base['ИМТ'] < 40.0) & (base['ИМТ'] >= 35.0)].count(),
                base['ИМТ'][base['ИМТ'] >= 40.0].count()
            ]
        })

    def circle_diag(base):
        fig, ax = plt.subplots(figsize=(12, 7), subplot_kw=dict(aspect="equal"), dpi= 80)
        data = base['Количество пипл']
        categories = base['Соответствие между массой человека и его ростом']
        explode = [0, 0, 0, 0, 0, 0, 0]

        def func(pct, allvals):
            absolute = int(pct/100.*np.sum(allvals))
            return "{:.1f}% ({:d} )".format(pct, absolute)

        wedges, texts, autotexts = ax.pie(data,
                                  autopct=lambda pct: func(pct, data),
                                  textprops=dict(color="w"),
                                  colors=plt.cm.Dark2.colors,
                                 startangle=140,
                                 explode=explode)

        # Decoration
        ax.legend(wedges, categories, title="Vehicle Class", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        plt.setp(autotexts, size=10, weight=700)
        ax.set_title("Class of Vehicles: Pie Chart")
        plt.show()

    circle_diag(int_info(male))
    circle_diag(int_info(fem))
