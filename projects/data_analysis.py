'''
Ohjelma kandin tulosten laskemista varten. 
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import typing
from tqdm import tqdm
import seaborn as sns
import tretsa
from matplotlib.patches import Ellipse
from scipy.stats import gaussian_kde
#import tretsa_utils # tutkimusryhmän kirjato
#import hrv_analysis # tutkimusryhmän kirjasto 
import astropy
import mpl_scatter_density # adds projection='scatter_density'
import wfdb
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import gridspec as grsp
from astropy.visualization import LogStretch
from astropy.visualization.mpl_normalize import ImageNormalize

def etsiAnnotaatiot(filename):
    path = '/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Kandi/st_episodit/'
    name = path + filename

    ann = wfdb.rdann(name, extension='stb')

    record_name = ann.record_name
    name = record_name + '_notes.csv'
    time = ann.sample
    note = ann.aux_note

    df = pd.DataFrame({'aika': time, 'merkintä': note})
    st_listi = []
    pituus_listi = []
    alku = 0
    loppu = 0

    for num in range(0,len(df)):
        row = df.loc[num]
        if '(' in row[1]:
            alku = df.loc[num][0]*0.001
            st_listi.append(alku)
            print('alku: ', alku)

        if ')' in row[1]:
            loppu = df.loc[num][0]*0.001
            st_listi.append(loppu)
            print('loppu:', loppu)
            print('')
        pituus_listi.append(loppu-alku)

    print('pisin episodi', max(pituus_listi))

    return st_listi

def periaate_poinacre():

    font = {'size' : 12}

    style = {'text.usetex' : True,
             'text.latex.preamble' : "\n".join([r"\usepackage[utf8]{inputenc}", 
             r"\usepackage[scaled=0.91]{helvet}", 
             r"\usepackage[T1]{fontenc}", 
             r"\renewcommand*\familydefault{\sfdefault}"])
            }

    plt.rc('font', **font)
    plt.rcParams.update(**style)
    cm=1/2.54

    rr = read_st_data('/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Kandi/min500nonst/s20011.4')

    rr_n = np.array(rr[:-1])
    rr_n1 = np.array(rr[1:])

    sd1 = float(np.std(np.subtract(rr_n, rr_n1) / np.sqrt(2)))
    sd2 = float(np.std(np.add(rr_n, rr_n1) / np.sqrt(2)))

    m = float(np.mean(rr))
    
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10*cm, 10*cm), constrained_layout=True)

    e1 = Ellipse((m, m), 2*sd1, 2*sd2, angle=-45, linewidth=1.2, fill=False, color="k")
    ax.scatter(rr_n, rr_n1,30,alpha=0.20,marker='h')

    plt.arrow(m, m, sd2 * np.sqrt(0.48), sd2 * np.sqrt(0.48), width=1, color="red", length_includes_head=True)
    plt.arrow(m, m, -sd1 * np.sqrt(0.30), sd1 * np.sqrt(0.30), width=1, color="orange", length_includes_head=True, head_length=3.5)
    #825, 820
    #750, 790
    plt.text(m + sd2 * np.sqrt(0.65), m + sd2 * np.sqrt(0.65), r"\textbf{SD2}", color="red")
    plt.text(750, 795, r"\textbf{SD1}", color="orange")
    plt.gca().add_patch(e1)
    ax.set_xlim([650,900])
    ax.set_ylim([650,900])
    plt.xlabel(r'RR$\mathrm{_n}$ (ms)')
    plt.ylabel(r'RR$\mathrm{_{n+1}}$ (ms)')

    plt.savefig('/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Kandi/poincare_periaate.pdf')
    plt.show()
    

def plot_poincare(num):
    rrst = analyse_all_files_in_folder('/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Kandi/min500nonst/',num)
    rrnonst = analyse_all_files_in_folder('/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Kandi/min500_nsrdb/',num)

    #terveet
    #rr = analyse_all_files_in_folder('/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Kandi/min500_nsrdb/',num)
    #rr = read_st_data(folder_path)

    rr_nst = np.array(rrst[:-1])    
    rr_n1st = np.array(rrst[1:])

    rr_nnonst = np.array(rrnonst[:-1])
    rr_n1nonst = np.array(rrnonst[1:])

    sd1st = float(np.std(np.subtract(rr_nst, rr_n1st) / np.sqrt(2)))
    sd2st = float(np.std(np.add(rr_nst, rr_n1st) / np.sqrt(2)))

    sd1nonst = float(np.std(np.subtract(rr_nnonst, rr_n1nonst) / np.sqrt(2)))
    sd2nonst = float(np.std(np.add(rr_nnonst, rr_n1nonst) / np.sqrt(2)))

    #m = float(np.mean(rr))
    #min_rr = float(np.min(rr))
    #max_rr = float(np.max(rr))

    font = {'size' : 12}

    style = {'text.usetex' : True,
             'text.latex.preamble' : "\n".join([r"\usepackage[utf8]{inputenc}", 
             r"\usepackage[scaled=0.91]{helvet}", 
             r"\usepackage[T1]{fontenc}", 
             r"\renewcommand*\familydefault{\sfdefault}"])
            }

    white_viridis = LinearSegmentedColormap.from_list('white_viridis', [
    (0, '#ffffff'),
    (1e-20, '#440053'),
    (0.2, '#404388'),
    (0.4, '#2a788e'),
    (0.6, '#21a784'),
    (0.8, '#78d151'),
    (1, '#fde624'),
    ], N=256)

    plt.rc('font', **font)
    plt.rcParams.update(**style)
    cm=1/2.54

    norm = ImageNormalize(vmin=20, vmax=8e3, stretch=LogStretch())

    fig = plt.figure(figsize=(15*cm,8*cm), constrained_layout=True)
    gs = grsp.GridSpec(2,2,fig,height_ratios=[1,16])

    ax1 = fig.add_subplot(gs[1,0],projection='scatter_density')
    density1 = ax1.scatter_density(rr_nst, rr_n1st, cmap=white_viridis, dpi=59, norm=norm, downres_factor=1)

    plt.xlabel(r'RR$\mathrm{_n}$ (ms)')
    plt.ylabel(r'RR$\mathrm{_{n+1}}$ (ms)')

    ax2 = fig.add_subplot(gs[1,1],projection='scatter_density', sharex=ax1)
    density2 = ax2.scatter_density(rr_nnonst, rr_n1nonst, cmap=white_viridis, dpi=38, norm=norm, downres_factor=1)
    # ST[20, 1e2, 1e3, 2e3, 4e3, 8e3]
    # terveet[4, 0.5e2, 1e3, 1.5e3, 3e3]
    #fig.colorbar(density2, label='Pisteiden määrä pikselissä', ticks=[4, 0.5e2, 1e3, 1.5e3, 3e3])
    #norm = ImageNormalize(vmin=4, vmax=3e3, stretch=LogStretch())
    # st vminmax20, 8e3
    # terveille vmimax 4, 3e3
    # stdpi 45
    # tervedpi 44
    ax1.set_yticks([200, 600, 1000, 1400])
    ax1.set_xticks([200, 600, 1000, 1400])
    ax2.set_yticks([200, 600, 1000, 1400])
    ax2.set_yticklabels('')
    ax1.set_xlim(200, 1600)
    ax1.set_ylim(200, 1600)    
    ax2.set_xlim(200, 1600)
    ax2.set_ylim(200, 1600)
    plt.xlabel(r'RR$\mathrm{_n}$ (ms)')

    cax = plt.subplot(gs[0,:])
    cbar = fig.colorbar(density2, label="Pisteiden määrä pikselissä" ,ticks=[20, 1e2, 1e3, 2e3, 4e3, 8e3], cax=cax, orientation='horizontal')
    cax.xaxis.set_ticks_position('top')
    cax.xaxis.set_label_position('top')
  
    plt.show()


def ddfa():
    file = '/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Kandi/ltstdb.h5'

    df = pd.read_hdf(file)
    #varikartta = plt.cm.get_cmap('viridis')
    font = {'size' : 12}

    style = {'text.usetex' : True,
             'text.latex.preamble' : "\n".join([r"\usepackage[utf8]{inputenc}", 
             r"\usepackage[scaled=0.91]{helvet}", 
             r"\usepackage[T1]{fontenc}", 
             r"\renewcommand*\familydefault{\sfdefault}"])
            }

    plt.rc('font', **font)
    plt.rcParams.update(**style)
    #s20301
    file = 's20561'
    episodi_leimat = etsiAnnotaatiot(file)

    df = df[df['file_id'] == file]
    df.reset_index(inplace=True)
    plt.rc('font', size=10)
 
    hrv_analysis.add_filtered_column(df, rr_key='rr_interval', method='diff', **{'threshold': 0.2})

    #fig, axs = plt.subplots(1, 2, constrained_layout=True, figsize=(16, 6), width_ratios=[6, 12])

    #axs[0].plot(df.time.values, df.rr_interval.values, markevery=np.argwhere(df.filtered.values).ravel(),mfc='r', mec='r', marker='x', label='RR')
    #axs[1].plot(df.time.values[~df['filtered']], df.rr_interval.values[~df['filtered']], c='orange')

    ddfa = tretsa_utils.dynamic_dfa(df, 5, 1, dfa_order=1, sort_key=None)
    #ddfa.to_csv('testitit.csv')
    #x_lim=[19874, 22500]
    #s20121 x_lim=[9623, 10000]
    #fig_size=(22,8)
    cm = 1/2.54
    #x_ts='time',
    #ts_data=df,
    #y_ts='beat_rate',

    DDFAfig = tretsa_utils.plots.plot_dynamic_alpha_landscape(ddfa,
    x_dfa='time',
    y_dfa='window_size',
    c_dfa='alpha',
    fig_size=(16*cm, 8*cm),
    legend_loc=None,
    x_lim=[5870, 11550]
    )

    #DDFAfig.set_size_inches(22,13)
    ax = DDFAfig.axes
    axx2 = ax[0].twiny()
    labelax = ax[0].twiny()
    axx2.set_xlabel('ST-episodi', loc='left')
    labelax.set_xlabel('ei ST-episodia', loc='right')
    ax[0].set_xlabel('Aika (s)')
    ax[0].set_ylabel('Skaala (RRI)')
    ax[1].set_ylabel(r'Skaalauseksponentti $\alpha$')
    #ax[2].set_ylabel('Syke (BPM)')

    # toka kuva vierekkäin viiva [21202]
    new_ticks = np.array(episodi_leimat)
    # ax[0] on ison kuvaajan x-akseli
    axx2.set_xlim(ax[0].get_xlim())
    #, alpha=0.4, linestyles='dotted'
    axx2.vlines([new_ticks], *ax[0].get_ylim(), color='red')
    axx2.set_xticks([])
    labelax.set_xticks([])
    plt.legend(frameon=False)

    plt.savefig('/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Kandi/DDFA' + file + 'z.pdf')
    #plt.show()

def histogram(num):
    path = '/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Kandi/min500_nsrdb/'
    files = os.listdir(path)
    list_of_subject_measures = []

    if num == 8:
        for file in tqdm(files):
            rri = read_st_data(path+file)
            sd1 = np.std(np.subtract(rri[:-1], rri[1:]) / np.sqrt(2))
            sd2 = np.std(np.add(rri[:-1], rri[1:]) / np.sqrt(2))
            SD = sd1/sd2
            list_of_subject_measures.append(SD)
    
    plt.hist(list_of_subject_measures)
    
    plt.show()



def hrv_series(num):
    #4,8s20011.4
    folder_path = '/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Kandi/min500_nsrdb/16265.1'
    df = read_st_data(folder_path)
    hrv_analysis.add_filtered_column(df, rr_key='rr_interval', method='diff', **{'threshold': 0.2})
    rr = df.rr_interval.values[~df['filtered']]

    plt.rc('font', size=20)
    #, facecolor='#4e008e'
    #fig, axs = plt.subplots(1, 2, constrained_layout=True, figsize=(16, 6), width_ratios=[6, 12])
    

    #rr = df['rr_interval']
    fig, ax = plt.subplots(figsize=(15, 10), constrained_layout=True)
    #ax.plot(df.time.values[~df['filtered']], df.rr_interval.values[~df['filtered']])
    ax.plot(rr, c='#4e008e')
    #ax.set_facecolor('#4e008e')
    #plt.axis('off')
    plt.ylabel('RR väli (ms)')
    plt.xlabel('n')
    #plt.ylim(400,1100)
    plt.savefig('/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Kandi/hrv_series.pdf')
    plt.show()

def dfa_alpha1(rr: typing.Union[np.ndarray, list], dfa_order: int = 2) -> float:
    """
    Tutkimusryhmän koodia
    Calculate DFA alpha1 in maximally overlapping windows
    Parameters
    ----------
    rr : list
        rr time series
    dfa_order : int
        DFA detrending order, currently implemented
        up to DFA 3 (can't calculate short scales for
        higher orders)

    Returns
    -------
    a : float
        DFA alpha1
    """
    if dfa_order < 3:
        scales = [4, 5, 6, 8, 10, 12, 14, 16]
    elif dfa_order == 3:
        scales = [5, 6, 8, 10, 12, 14, 16]
    fs, ls = tretsa.MF_DFA(rr, q=2, return_logarithms=True, ls=scales,
                           window_step=1, dfa_order=dfa_order)
    a, *_ = tretsa.util.line_fit(ls, fs)
    return a

def dfa_alpha2(rr: typing.Union[np.ndarray, list], dfa_order: int = 2) -> float:
    """
    Tutkimusryhmän koodia
    Calculate DFA alpha1 in maximally overlapping windows
    Parameters
    ----------
    rr : list
        rr time series
    dfa_order : int
        DFA detrending order, currently implemented
        up to DFA 3 (can't calculate short scales for
        higher orders)

    Returns
    -------
    a : float
        DFA alpha1
    """
    #[4, 5, 6, 8, 10, 12, 14, 16]
    if dfa_order < 3:
        scales = [16, 24, 30, 36, 42, 48, 54, 64]
    elif dfa_order == 3:
        scales = [5, 6, 8, 10, 12, 14, 16]
    fs, ls = tretsa.MF_DFA(rr, q=2, return_logarithms=True, ls=scales,
                           window_step=1, dfa_order=dfa_order)
    a, *_ = tretsa.util.line_fit(ls, fs)
    return a

def ordinary_dfa_alpha1(data: np.ndarray) -> float:
    """
    Tutkimusryhmän koodia
    Calculate ordinary DFA alpha1
    Parameters
    ----------
    data : np.ndarray
        data for DFA
    plots : bool
        If True do some plotting

    Returns
    -------
    a : float
        DFA alpha-1
    """
    logFs, logls = tretsa.DFA(data, num_ls=50, return_logarithms=True)

    alfa1_limit = np.searchsorted(logls, 1.21)

    a, b, a_std, r2 = tretsa.util.line_fit(logls[:alfa1_limit], logFs[:alfa1_limit])

    return a

def ordinary_dfa_alpha2(data: np.ndarray) -> float:
    """
    Tutkimusryhmän koodia
    Calculate ordinary DFA alpha2
    Parameters
    ----------
    data : np.ndarray
        data for DFA
    plots : bool
        If True do some plotting

    Returns
    -------
    a : float
        DFA alpha-2
    """
    logFs, logls = tretsa.DFA(data, num_ls=50, return_logarithms=True)

    alfa2_limit1 = np.searchsorted(logls, 1.2)
    alfa2_limit2 = np.searchsorted(logls, 1.81)

    a, b, a_std, r2 = tretsa.util.line_fit(logls[alfa2_limit1:alfa2_limit2], logFs[alfa2_limit1:alfa2_limit2])
    
    return a

def read_st_data(path: str):
    """
    Tutkimusryhmän koodia
    Lukee csv tiedoston pandan dataframeen (vähä niinku Pythonin Excel,
    taulokkumuotoisen datan käsittelyyn tarkoitettu siis)
    Parameters
    ----------
    path : str
        tiedostopolku csv tiedostoon
    Returns
    -------
    data : pd.DataFrame
    """
    return pd.read_csv(path, usecols=[1], sep=' ', names=['rr_interval'])


def figures(num):
    stdata = analyse_all_files_in_folder('/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Kandi/min500/', num)
    nonstdata = analyse_all_files_in_folder('/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Kandi/min500nonst/', num)
    healthy = analyse_all_files_in_folder('/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Kandi/min500_nsrdb/', num)
    nimi = 'Ryhmä'
    stdata[nimi] = 'ST-episodi'
    nonstdata[nimi] = 'ST'
    healthy[nimi] = 'Terveet'

    font = {'size' : 12}

    style = {'text.usetex' : True,
             'text.latex.preamble' : "\n".join([r"\usepackage[utf8]{inputenc}", 
             r"\usepackage[scaled=0.91]{helvet}", 
             r"\usepackage[T1]{fontenc}", 
             r"\renewcommand*\familydefault{\sfdefault}"])
            }

    plt.rc('font', **font)
    plt.rcParams.update(**style)
    cm = 1/2.54

    df = pd.concat([stdata, nonstdata, healthy])
    # tehdään kuva, jossa on monta erillistä kuvaajaa ja hieman nättiä muotoilua
    if num == 1:
        fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(15*cm, 12*cm), constrained_layout=True, sharex=True)
        axs = axs.flatten()
    
    if num == 9:
        fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(15*cm, 12*cm), constrained_layout=True, sharex=True)
        axs = axs.flatten()

    if num == 2:
        fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(15*cm, 10*cm), constrained_layout=True)
        axs = axs.flatten()

    if num == 4:
        fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(15*cm,10*cm), constrained_layout=True)


    for i, col in enumerate(df.columns):
        if col not in [nimi, 'segment']:
                axs[i] = sns.boxplot(data=df, x=nimi, y=col, ax=axs[i])
        

    if num == 1:
        axs[0].set_ylim(400, 1300)
        axs[0].set_ylabel('mRR (ms)')
        axs[1].set_ylim(0, 500)
        axs[1].set_ylabel('stdRR (ms)')
        axs[2].set_ylim(0, 100)
        axs[2].set_ylabel(r'pRR20 (\%)')
        axs[3].set_ylim(0, 2)
        axs[3].set_ylabel('SD1/SD2 RR (ms)')
        for axn in axs:
            axn.set_xlabel('')
        #SD1 ja SD2 arvojen piirtämiseen
        #axs[3].set_ylim(0,500)
        #axs[2].set_ylim(0,300)
        plt.savefig('/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Kandi/time_domain.pdf')
    if num == 2:
        for axn in axs:
            axn.set_xlabel('')
        axs[0].set_ylabel("DFA-" + r"$\alpha_1$")
        axs[1].set_ylabel("DFA-" + r"$\alpha_2$")
        plt.savefig('/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Kandi/DFA1_DFA2.pdf')
    if num == 4:
        for axn in axs:
            axn.set_xlabel('')
        #plt.ylabel('DFA (2. asteen sovite)')
        plt.savefig('/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Kandi/DFAx2.pdf')
    if num ==9:
        for axn in axs:
            axn.set_xlabel('')
        axs[0].set_ylabel("DFA1-" + r"$\alpha_1$")
        axs[1].set_ylabel("DFA1-" + r"$\alpha_2$")
        axs[2].set_ylabel("DFA2-" + r"$\alpha_1$")
        axs[3].set_ylabel("DFA2-" + r"$\alpha_2$")
        plt.savefig('/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Kandi/kaikki_DFAt.pdf')
    
    plt.show()
    

def analyse_all_files_in_folder(folder_path, num):
    files = os.listdir(folder_path)
    list_of_subject_measures = []
    list2 = []
    list3 = []
    list4 = []

    if num == 2:
        for file in tqdm(files):
            rr_df = read_st_data(folder_path+file)

            dfaMeasure = ordinary_dfa_alpha1(rr_df.rr_interval.to_numpy())
            list_of_subject_measures.append(dfaMeasure)

        for file in tqdm(files):
            rr_df = read_st_data(folder_path+file)

            dfaMeasure = ordinary_dfa_alpha2(rr_df.rr_interval.to_numpy())
            list2.append(dfaMeasure)

        measures = {
            "DFA1-" + r"$\alpha_1$" : list_of_subject_measures,
            "DFA1-" + r"$\alpha_2$" : list2
        }
        
        result_df = pd.DataFrame(measures)

    if num == 4:
        for file in tqdm(files):
            rr_df = read_st_data(folder_path+file)

            dfaMeasure = dfa_alpha1(rr_df.rr_interval.to_numpy())
            list_of_subject_measures.append(dfaMeasure)
        
        for file in tqdm(files):
            rr_df = read_st_data(folder_path+file)

            dfaMeasure = dfa_alpha2(rr_df.rr_interval.to_numpy())
            list2.append(dfaMeasure)
        measures = {
            'DFA2-' + r'$\alpha_1$': list_of_subject_measures,
            'DFA2-' + r'$\alpha_2$' : list2
        }
        result_df = pd.DataFrame(measures)

    if num == 1:
        for file in tqdm(files):
            rr_df = read_st_data(folder_path+file)
            time_domain_measures_df = compute_time_domain_measures(rr_df.rr_interval.to_numpy())
            #time_domain_measures_df['segment'] = file
            list_of_subject_measures.append(time_domain_measures_df)
        
        result_df = pd.concat(list_of_subject_measures)

    if num == 3:
        for file in tqdm(files):
            rr_df = read_st_data(folder_path+file)
            list_of_subject_measures.append(rr_df)

        result_df = pd.concat(list_of_subject_measures)

    if num == 9:
        for file in tqdm(files):
            rr_df = read_st_data(folder_path+file)

            dfaMeasure = ordinary_dfa_alpha1(rr_df.rr_interval.to_numpy())
            list_of_subject_measures.append(dfaMeasure)

        for file in tqdm(files):
            rr_df = read_st_data(folder_path+file)

            dfaMeasure = ordinary_dfa_alpha2(rr_df.rr_interval.to_numpy())
            list2.append(dfaMeasure)

        for file in tqdm(files):
            rr_df = read_st_data(folder_path+file)

            dfaMeasure = dfa_alpha1(rr_df.rr_interval.to_numpy())
            list3.append(dfaMeasure)
        
        for file in tqdm(files):
            rr_df = read_st_data(folder_path+file)

            dfaMeasure = dfa_alpha2(rr_df.rr_interval.to_numpy())
            list4.append(dfaMeasure)
        measures = {
            "DFA1-" + r"$\alpha_1$" : list_of_subject_measures,
            "DFA1-" + r"$\alpha_2$" : list2,
            'DFA2-' + r'$\alpha_1$': list3,
            'DFA2-' + r'$\alpha_2$' : list4
        }
        result_df = pd.DataFrame(measures)

    return result_df


def compute_time_domain_measures(rri: typing.Union[np.ndarray, list]) -> dict:
    """
    Tutkimusryhmän koodia
    Compute basic HRV measures from np.array into pandas dataframe
    Parameters
    ----------
    rri : np.array
        RR intervals in milliseconds (ms)
    Returns
    -------
    measures : dict
        Dictionary of the given HRV measures
    """
    mRR = np.nanmean(rri)
    stdRR = np.nanstd(rri)
    diffs = np.diff(rri)
    sd1 = np.std(np.subtract(rri[:-1], rri[1:]) / np.sqrt(2))
    sd2 = np.std(np.add(rri[:-1], rri[1:]) / np.sqrt(2))
    measures = {
        'mRR (ms)': mRR,
        'stdRR (ms)': stdRR,
        #'CVRR': stdRR * 100 / mRR,
        #'rmssd RR': np.sqrt(np.nanmean(diffs**2)),
        'pRR20 (%)': np.nanmean(np.fabs(diffs) > 20) * 100,
        #'pRR50': np.nanmean(np.fabs(diffs) > 50) * 100,
        # poincare measures
        #'SD1 RR': sd1,
        #'SD2 RR': sd2,
        'SD1/SD2 RR (ms)': sd1/sd2,
    }
    return pd.DataFrame([measures])

def main():

    num = input("Time domain 1, DFA 2, Poincare 3, DFA2 4, DDFA 5, HRVsarja 6, Annotaatiot 7, Kaikka DFAt 9, Periaate poincare 10: ")
    num = int(num)
    
     
    if num == 3:
        plot_poincare(num)
        return
    if num == 5:
        ddfa()
        return
    if num == 6:
        hrv_series(num)
        return
    if num == 7:
        path = '/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Kandi/st_episodit/'
        names = os.listdir(path)
        for file in names:
            print(file)
            if file == ".DS_Store":
                continue
            file = file.replace(".stb", "")
            etsiAnnotaatiot(file)
        return
    if num == 8:
        histogram(num)
        return
    if num == 10:
        periaate_poinacre()
        return
    figures(num)


if __name__ == '__main__':
    main()