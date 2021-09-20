# -*- coding: utf-8 -*-
import os
import shutil
from jinja2 import Environment, FileSystemLoader
from pyecharts.charts import Pie
from pyecharts.options import InitOpts, LegendOpts, TooltipOpts, TitleOpts


class Render:
    """
    Render module as html.
    """
    def __init__(self):
        __file__path = os.path.dirname(__file__)
        self.env = Environment(
            loader=FileSystemLoader(
                os.path.join(
                    os.path.abspath(__file__path), 'template'
                )
            )
        )
        self.report_dir = 'report'
        self.page_dir = 'page'
        os.makedirs(self.report_dir, exist_ok=True)
        os.chdir(self.report_dir)
        for directory in ['js', 'css']:
            if os.path.exists(directory):
                shutil.rmtree(directory)
            shutil.copytree(os.path.join(os.path.abspath(__file__path), directory), directory)

    def render(self, summary, section_group_sizes, formatted_modules):
        # Render summary page
        _, summary_file = self._render_page(
            self.template_summary,
            'Summary', self.page_dir,
            **{'title': 'Summary',
               'table': SummaryTable(summary),
               'section_group_sizes': section_group_sizes.values,
               'pie_module':
                   self._render_chart_pie('modules', 'module', list(summary['TOTAL'][:-1].to_dict().items())),
               'pie_section':
                   self._render_chart_pie('sections', 'section', list(summary.loc['TOTAL'][:-1].to_dict().items()))
               }
        )
        # Render module detail pages
        module_files = []
        for name, details in formatted_modules.items():
            _, file = self._render_page(
                self.template_detail,
                name, self.page_dir,
                **{'title': name,
                   'tables': map(lambda k, v: (k, Table(v)), details.keys(), details.values())
                   }
            )
            module_files.append(file)
        # Finally render the main report page
        self._render_page(
            self.template_report,
            'Report',
            **{'title': 'Report',
               'modules':
                   [('Summary', summary_file)] +
                   list(map(lambda k, f: (k, f), formatted_modules.keys(), module_files))
               }
        )

    def _render_page(self, template, output_name=None, output_dir='.', **model_kwargs):
        html = template.render(**model_kwargs)
        output_file = None
        if output_name:
            output_file = os.path.join(output_dir, self.normalize_file_name(output_name))
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w+', encoding="utf-8") as file:
                file.write(html)
        return html, output_file

    def _render_chart_pie(self, title, series_name, series_data_pairs):
        html = Pie(InitOpts(height='60%', width='60%', theme=''))\
            .set_global_opts(
            title_opts=TitleOpts(title=title, pos_left='center'),
            legend_opts=LegendOpts(type_='scroll', orient='vertical', pos_top='middle', pos_right='0', padding=[50, 0]),
            tooltip_opts=TooltipOpts(formatter='{a} <br/>{b} : {c} ({d}%)'))\
            .add(series_name=series_name, data_pair=series_data_pairs)\
            .render_embed('pie.html', env=self.env)
        return html

    @staticmethod
    def normalize_file_name(name):
        return name.strip('*') + '.html'  # Strip special char not be allowed in the path.

    @property
    def template_report(self):
        template = self.__dict__.get('__template_report')
        if not template:
            template = self.env.get_template('report.html')
            self.__setattr__('__template_report', template)
        return template

    @property
    def template_summary(self):
        template = self.__dict__.get('__template_summary')
        if not template:
            template = self.env.get_template('summary.html')
            self.__setattr__('__template_summary', template)
        return template

    @property
    def template_detail(self):
        template = self.__dict__.get('__template_detail')
        if not template:
            template = self.env.get_template('detail.html')
            self.__setattr__('__template_detail', template)
        return template


class Table:
    """
    Iterate over the title bar and rows of table data.
    """
    def __init__(self, data_source):
        self.data_source = data_source

    def __iter__(self):
        yield self.data_source.columns
        for row in self.data_source.values:
            yield row


class SummaryTable(Table):
    """
    Iterate over the title bar and rows of table data with row header.
    """
    def __init__(self, data_source):
        super().__init__(data_source)

    def __iter__(self):
        title_column = [''] + list(self.data_source.index)
        i = 0
        for row in super().__iter__():
            yield self._row(title_column[i], row)
            i = i + 1

    @staticmethod
    def _row(title, row):
        yield title
        for val in row:
            yield val
