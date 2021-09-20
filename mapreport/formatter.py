# -*- coding: utf-8 -*-
from collections import OrderedDict
from pandas import DataFrame
import logging


class Formatter:
    """
    Format the module as a table, merge and count the section.
    Summarize all modules as a table.
    """
    def __init__(self):
        pass

    @staticmethod
    def format_module(modules, sections):
        formatted_module_dict = OrderedDict()
        for module, objects in modules.items():
            formatted_module_dict[module] = OrderedDict()
            formatted_module_dict[module]['overview'] =\
                data_df = DataFrame([[0] * len(sections)] * (len(objects)), columns=sections, index=objects.keys())
            # Add section size to each object
            for _object, _sections in objects.items():
                df = DataFrame(_sections, columns=['section', 'address', 'size', 'sub_section'])
                sizes = df.groupby('section', sort=False).sum()
                for section, size in sizes.iterrows():
                    data_df.at[_object, section] = size
            # Add row TOTAL
            data_df.loc['TOTAL'] = data_df.sum()
            # Add column TOTAL
            data_df['TOTAL'] = data_df.sum(axis=1)
            # Add column OBJECT
            data_df['OBJECT'] = list(objects.keys()) + ['TOTAL']

        # Add 'fill' details for each section of 'fill' module
        fills = formatted_module_dict.get('*fill*', None)
        if fills:
            groups = DataFrame(modules['*fill*']['*fill*'], columns=['section', 'address', 'size', 'sub_section'])\
                .groupby('section', sort=False)
            for section, df in groups:
                sizes = df.groupby('sub_section', sort=False).sum()
                sizes['SECTION'] = sizes.index
                sizes.loc['TOTAL'] = [sizes['size'].sum(), 'TOTAL']
                sizes.rename(columns={'size': '*fill*'}, inplace=True)
                fills[section] = sizes
        return formatted_module_dict

    @staticmethod
    def summary_module(formatted_modules):
        data = [df.loc['TOTAL'][:-2] - df.loc['*fill*'][:-2] if m != '*fill*' and '*fill*' in df['OBJECT'] else
                df.loc['TOTAL'][:-2] for m, df in ((m, detail['overview']) for m, detail in formatted_modules.items())]
        summary_df = DataFrame(data, index=formatted_modules.keys())
        # Add column *fill* if exists
        if '*fill*' in formatted_modules:
            summary_df['*fill*'] = [df.at['*fill*', 'TOTAL'] if m != '*fill*' and '*fill*' in df['OBJECT'] else 0
                                    for m, df in ((m, detail['overview']) for m, detail in formatted_modules.items())]
        # Add column TOTAL
        summary_df['TOTAL'] = summary_df.sum(axis=1)
        # Add row TOTAL
        summary_df.loc['TOTAL'] = summary_df.sum()
        # Check TOTAL
        total_column, total_row = summary_df.at['TOTAL', 'TOTAL'], summary_df.loc['TOTAL'][:-1].sum()
        if total_row != total_column:
            logging.ERROR('total_column(%d) != total_row(%d). Please report a bug!' % (total_column, total_row))
            raise Exception('total_column(%d) != total_row(%d)' % (total_column, total_row))
        return summary_df

    @staticmethod
    def group_section(summary, section_group_dict, sections_effective, sections_empty):
        grouped_set = set()
        df = DataFrame(columns=['group', 'size'])
        for group, sections in section_group_dict.items():
            section_list = []
            for section in sections:
                if section in sections_effective:
                    section_list.append(section)
                elif section not in sections_empty:
                    logging.warning('Section "%s" specified by group "%s" does not exists!' % (section, group))
            df = df.append({'group': group,
                            'size': Formatter.get_human_size(
                                summary[section_list].loc['TOTAL'].sum())
                            },
                           ignore_index=True
                           )
            grouped_set.update(section_list)
        # Prompt sections that have not been grouped
        diff = set(sections_effective) - grouped_set
        if diff:
            logging.info('Section %s not be grouped.' % diff)
        return df

    HUMAN_SIZE_LIST = [[10000, lambda size: '%dB' % size],
                       [1024*1024, lambda size: '%.3fKB' % (size/1024)],
                       [1024*1024*1024, lambda size: '%.3fMB' % (size/(1024*1024))],
                       [1024*1024*1024*1024, lambda size: '%.3fGB' % (size/(1024*1024*1024))]]

    @staticmethod
    def get_human_size(size):
        for limit, func in Formatter.HUMAN_SIZE_LIST:
            if size < limit:
                return func(size)
        return Formatter.HUMAN_SIZE_LIST[-1][1](size)
