import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import requests
import seaborn as sns
import warnings
import statsmodels.formula.api as smf

warnings.filterwarnings(action='once')

large = 22
med = 16
small = 12
params = {'legend.fontsize': med,
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

if __name__ == '__main__':
    path = 'https://raw.githubusercontent.com/go95/student_files/main/Рмэз_2016.csv'
    filereq = requests.get(path)
    with open('log.csv', 'w') as file:
        file.write(filereq.text)

    data = pd.read_csv('log.csv', index_col=False)
    df = pd.DataFrame.from_records(data)
    base = df[['um1', 'um2', 'uj10', 'u_age', 'uh5', 'status']]
    base = base[(base.um1 < 99999997.0) &
                (base.um2 < 99999997.0) &
                (base.uj10 < 99999997.0) &
                (base.u_age >= 19) &
                (base.u_age <= 72)]
    base['ИМТ'] = base.um1 / (base.um2 * base.um2 / 10000)
    base['Логарифм'] = np.log(base.uj10)
    base.columns = ['Вес', 'Рост', 'З/п', 'Возраст', 'Пол', 'Тип насел пункта', 'ИМТ', 'Логарифм_зп']

    male = base[['Пол', 'ИМТ']][base.Пол == 1]
    fem = base[['Пол', 'ИМТ']][base.Пол == 2]


    def int_info(mur):
        return pd.DataFrame({
            'Соответствие между массой человека и его ростом': [
                'Выраженный дефицит массы',
                'Недостаточная масса тела',
                'Норма',
                'Предожирение',
                'Ожирение',
                'Ожирение резкое',
                'Очень резкое ожирение'
            ],
            'Количество пипл': [
                mur['ИМТ'][mur['ИМТ'] < 16.0].count(),
                mur['ИМТ'][(mur['ИМТ'] < 18.5) & (mur['ИМТ'] >= 16.0)].count(),
                mur['ИМТ'][(mur['ИМТ'] < 25.0) & (mur['ИМТ'] >= 18.5)].count(),
                mur['ИМТ'][(mur['ИМТ'] < 30.0) & (mur['ИМТ'] >= 25.0)].count(),
                mur['ИМТ'][(mur['ИМТ'] < 35.0) & (mur['ИМТ'] >= 30.0)].count(),
                mur['ИМТ'][(mur['ИМТ'] < 40.0) & (mur['ИМТ'] >= 35.0)].count(),
                mur['ИМТ'][mur['ИМТ'] >= 40.0].count()
            ]
        })


    def circle_diag(meow, title):
        fig, ax = plt.subplots(figsize=(12, 7), subplot_kw=dict(aspect="equal"), dpi=80)
        data = meow['Количество пипл']
        categories = meow['Соответствие между массой человека и его ростом']
        explode = [0, 0, 0, 0, 0, 0, 0]

        def func(pct, allvals):
            absolute = int(pct / 100. * np.sum(allvals))
            return "{:.1f}% ({:d} )".format(pct, absolute)

        wedges, texts, autotexts = ax.pie(data,
                                          autopct=lambda pct: func(pct, data),
                                          textprops=dict(color="w"),
                                          startangle=180,
                                          explode=explode)

        # Decoration
        ax.legend(wedges, categories, title="Вердикт", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        plt.setp(autotexts, size=10, weight=700)
        ax.set_title("Состояние телосложения среди опрошенных " + title)
        plt.show()


    circle_diag(int_info(male), 'мужчин')
    circle_diag(int_info(fem), "женщин")
    regress = base[['Логарифм_зп', 'ИМТ', 'Возраст']]
    regress['ИМТ'] = regress['ИМТ']**2
    regress['Возраст'] = regress['Возраст']**2

    model1 = smf.ols(formula='Логарифм_зп ~ ИМТ + Возраст', data=regress).fit()
    # sns.lmplot('Возраст', 'ИМТ', hue='Логарифм_зп', data=regress)
    # plt.show()
    print(model1.summary())


