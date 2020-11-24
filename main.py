# matplotlib==3.2.2
# numpy==1.19.3
# pandas==1.1.4

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
import seaborn as sns
import warnings
import statsmodels.formula.api as smf

warnings.filterwarnings(action='once')
pd.options.mode.chained_assignment = None
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

if __name__ == '__main__':
    # parse
    path = 'https://raw.githubusercontent.com/go95/student_files/main/Рмэз_2016.csv'
    filereq = requests.get(path)
    with open('log.csv', 'w') as file:
        file.write(filereq.text)
    data = pd.read_csv('log.csv', index_col=False)

    # cleaning
    df = pd.DataFrame.from_records(data)
    base = df[['um1', 'um2', 'uj10', 'u_age', 'uh5', 'status']]
    base = base[(base.um1 < 99999997.0) &
                (base.um2 < 99999997.0) &
                (base.uj10 < 99999997.0) &
                (base.u_age >= 19) &
                (base.u_age <= 72)]
    base['ИМТ'] = base.um1 / (base.um2 * base.um2 / 10000)
    base['Логарифм'] = np.log(base.uj10)
    base.columns = ['Вес', 'Рост', 'З/п', 'Возраст', 'Пол', 'Тип', 'ИМТ', 'Логарифм_зп']

    # circle diagrams
    def int_info(mur):
        return pd.DataFrame({
            'Телосложение': [
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
        categories = meow['Телосложение']
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

    male = base[['Пол', 'ИМТ']][base.Пол == 1]
    fem = base[['Пол', 'ИМТ']][base.Пол == 2]
    circle_diag(int_info(male), 'мужчин')
    circle_diag(int_info(fem), "женщин")

    # regression
    regress = base[['Логарифм_зп', 'ИМТ', 'Возраст']]
    regress.loc['ИМТ'] = regress['ИМТ'] ** 2
    regress.loc['Возраст'] = regress['Возраст'] ** 2

    model1 = smf.ols(formula='Логарифм_зп ~ ИМТ + Возраст', data=regress).fit()
    # sns.lmplot('Возраст', 'ИМТ', hue='Логарифм_зп', data=regress)
    # plt.show()
    print(model1.summary())

    # Histogram
    last = base[['ИМТ', 'Возраст', 'Пол', 'Тип']]
    last['Телосложение'] = 'Выраженный дефицит массы'
    last.loc[last.ИМТ >= 16.0, 'Телосложение'] = 'Недостаточная масса тела'
    last.loc[last.ИМТ >= 18.5, 'Телосложение'] = 'Норма'
    last.loc[last.ИМТ >= 25.0, 'Телосложение'] = 'Норма-предожирение'
    last.loc[last.ИМТ >= 30.0, 'Телосложение'] = 'Ожирение'
    last.loc[last.ИМТ >= 35.0, 'Телосложение'] = 'Ожирение резкое'
    last.loc[last.ИМТ >= 40.0, 'Телосложение'] = 'Очень резкое ожирение'

    x_var, groupby_var = 'Возраст', 'Телосложение'
    df_agg = last.loc[:, [x_var, groupby_var]].groupby(groupby_var)
    vals = [last[x_var].values.tolist() for i, last in df_agg]

    plt.figure(figsize=(16, 9), dpi=80)
    colors = [plt.cm.Spectral(i / float(len(vals) - 1)) for i in range(len(vals))]
    n, bins, patches = plt.hist(vals, 10, stacked=True, density=False, color=colors[:len(vals)])

    plt.legend({group: col for group, col in zip(np.unique(last[groupby_var]).tolist(), colors[:len(vals)])})
    plt.title(f"Гистограмма возраста опрошенных, разбитая по оценке телосложения", fontsize=22)
    plt.xlabel(x_var)
    plt.ylabel("Количество опрошенных")
    plt.xticks(ticks=bins[::1], labels=[round(b, 1) for b in bins[::1]])

    # multi param plots
    def semidata(num):
        plt.plot(last[last['Тип'] == num].groupby(x_var).mean().index, 'ИМТ',
                 data=last[last['Тип'] == num].groupby(x_var).mean()
                 )

    last['Лока'] = 'Областной центр'
    last.loc[last.Тип == 2, 'Лока'] = 'Город'
    last.loc[last.Тип == 3, 'Лока'] = 'ПГТ'
    last.loc[last.Тип == 4, 'Лока'] = 'Село'

    df_agg = last.loc[:, ['Возраст', 'Лока']].groupby('Лока')
    vals = [last['Возраст'].values.tolist() for i, last in df_agg]
    colors = [plt.cm.Spectral(i / float(len(vals) - 1)) for i in range(len(vals))]
    plt.figure(figsize=(16, 9), dpi=80)
    for i in range(4):
        semidata(float(i + 1))
    plt.legend({group: col for group, col in zip(np.unique(last['Лока']).tolist(), colors[:len(vals)])})
    plt.title("Кореляция ИМТ от возраста в зависимости от локации", fontsize=22)
    plt.xticks(ticks=bins[::1], labels=[round(b, 1) for b in bins[::1]],
               horizontalalignment='center')
    plt.ylabel("Средний ИМТ")
    plt.xlabel("Возраст")
    plt.grid()
    plt.show()
