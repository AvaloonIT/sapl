from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Button, Column, Fieldset, Layout, Submit
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

import crispy_layout_mixin
import sapl
from crispy_layout_mixin import form_actions
from norma.models import LegislacaoCitada, TipoNormaJuridica
from sapl.settings import MAX_DOC_UPLOAD_SIZE

from .models import (AcompanhamentoMateria, Anexada, Autor, Autoria,
                     DespachoInicial, DocumentoAcessorio, MateriaLegislativa,
                     Numeracao, Proposicao, Relatoria, StatusTramitacao,
                     TipoMateriaLegislativa, Tramitacao, UnidadeTramitacao)

ORDENACAO_MATERIAIS = [(1, 'Crescente'),
                       (2, 'Decrescente')]


def em_tramitacao():
    return [('', 'Tanto Faz'),
            (True, 'Sim'),
            (False, 'Não')]


class ProposicaoForm(ModelForm):

    tipo_materia = forms.ModelChoiceField(
        label=_('Matéria Vinculada'),
        required=False,
        queryset=TipoMateriaLegislativa.objects.all(),
        empty_label='Selecione',
    )

    numero_materia = forms.CharField(
        label='Número', required=False)

    ano_materia = forms.CharField(
        label='Ano', required=False)

    def clean_texto_original(self):
        texto_original = self.cleaned_data.get('texto_original', False)
        if texto_original:
            if texto_original.size > MAX_DOC_UPLOAD_SIZE:
                raise ValidationError("Arquivo muito grande. ( > 5mb )")
            return texto_original

    class Meta:
        model = Proposicao
        fields = ['tipo', 'data_envio', 'descricao', 'texto_original']

    def __init__(self, excluir=False, *args, **kwargs):
        more = []
        if excluir:
            more = [Submit('Excluir', 'Excluir')]

        row1 = crispy_layout_mixin.to_row(
            [('tipo', 8), ('data_envio', 4)])
        row2 = crispy_layout_mixin.to_row(
            [('descricao', 12)])
        row3 = crispy_layout_mixin.to_row(
            [('tipo_materia', 4), ('numero_materia', 4), ('ano_materia', 4)])
        row4 = crispy_layout_mixin.to_row(
            [('texto_original', 12)])

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(_('Incluir Proposição'),
                     row1, row2, row3, row4,
                     form_actions(more=more))
        )
        super(ProposicaoForm, self).__init__(
            *args, **kwargs)


class AcompanhamentoMateriaForm(ModelForm):

    class Meta:
        model = AcompanhamentoMateria
        fields = ['email']

    def __init__(self, *args, **kwargs):

        row1 = crispy_layout_mixin.to_row([('email', 10)])

        row1.append(
            Column(form_actions(save_label='Cadastrar'), css_class='col-md-2')
        )

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Acompanhamento de Matéria por e-mail'), row1
            )
        )
        super(AcompanhamentoMateriaForm, self).__init__(*args, **kwargs)


class DocumentoAcessorioForm(ModelForm):
    autor = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = DocumentoAcessorio
        fields = ['tipo',
                  'nome',
                  'data',
                  'autor',
                  'ementa']
        widgets = {
            'data': forms.DateInput(attrs={'class': 'dateinput'})
        }

    def clean_autor(self):
        autor_field = self.cleaned_data['autor']
        try:
            int(autor_field)
        except ValueError:
            return autor_field
        else:
            if autor_field:
                return str(Autor.objects.get(id=autor_field))

    def __init__(self, excluir=False, *args, **kwargs):

        row1 = crispy_layout_mixin.to_row(
            [('tipo', 4), ('nome', 4), ('data', 4)])

        row2 = crispy_layout_mixin.to_row(
                 [('autor', 0),
                  (Button('pesquisar',
                          'Pesquisar Autor',
                          css_class='btn btn-primary btn-sm'), 2),
                  (Button('limpar',
                          'Limpar Autor',
                          css_class='btn btn-primary btn-sm'), 10)])

        row3 = crispy_layout_mixin.to_row(
            [('ementa', 12)])

        more = []
        if excluir:
            more = [Submit('Excluir', 'Excluir')]

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Incluir Documento Acessório'),
                row1,
                HTML(sapl.utils.autor_label),
                HTML(sapl.utils.autor_modal),
                row2, row3,
                form_actions(more=more)
            )
        )
        super(DocumentoAcessorioForm, self).__init__(*args, **kwargs)


class RelatoriaForm(ModelForm):

    class Meta:
        model = Relatoria
        fields = ['data_designacao_relator',
                  'comissao',
                  'parlamentar',
                  'data_destituicao_relator',
                  'tipo_fim_relatoria'
                  ]
        widgets = {
            'data_designacao_relator': forms.DateInput(attrs={
                'class': 'dateinput'}),
            'data_destituicao_relator': forms.DateInput(attrs={
                                                        'class': 'dateinput'}),
        }


class TramitacaoForm(ModelForm):
    urgente = forms.ChoiceField(required=False,
                                label='Tramitando',
                                choices=[(True, 'Sim'), (False, 'Não')],
                                widget=forms.Select(
                                  attrs={'class': 'selector'}))
    class Meta:
        model = Tramitacao
        fields = ['data_tramitacao',
                  'unidade_tramitacao_local',
                  'status',
                  'turno',
                  'urgente',
                  'unidade_tramitacao_destino',
                  'data_encaminhamento',
                  'data_fim_prazo',
                  'texto']

    def __init__(self, excluir=False, *args, **kwargs):
        row1 = crispy_layout_mixin.to_row(
            [('data_tramitacao', 6), ('unidade_tramitacao_local', 6)])

        row2 = crispy_layout_mixin.to_row(
            [('status', 5), ('turno', 5), ('urgente', 2)])

        row3 = crispy_layout_mixin.to_row(
            [('unidade_tramitacao_destino', 12)])

        row4 = crispy_layout_mixin.to_row(
            [('data_encaminhamento', 6), ('data_fim_prazo', 6)])

        row5 = crispy_layout_mixin.to_row(
            [('texto', 12)])

        more = []
        if excluir:
            more = [Submit('Excluir', 'Excluir')]
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(_('Incluir Tramitação'),
                     row1, row2, row3, row4, row5,
                     ),
            form_actions(more=more)
        )
        super(TramitacaoForm, self).__init__(
            *args, **kwargs)


class LegislacaoCitadaForm(ModelForm):

    tipo = forms.ModelChoiceField(
        label=_('Tipo Norma'),
        required=True,
        queryset=TipoNormaJuridica.objects.all(),
        empty_label='Selecione',
    )

    numero = forms.CharField(label='Número', required=True)

    ano = forms.CharField(label='Ano', required=True)

    disposicao = forms.CharField(label='Disposição', required=False)

    parte = forms.CharField(label='Parte', required=False)

    livro = forms.CharField(label='Livro', required=False)

    titulo = forms.CharField(label='Título', required=False)

    capitulo = forms.CharField(label='Capítulo', required=False)

    secao = forms.CharField(label='Seção', required=False)

    subsecao = forms.CharField(label='Subseção', required=False)

    artigo = forms.CharField(label='Artigo', required=False)

    paragrafo = forms.CharField(label='Parágrafo', required=False)

    inciso = forms.CharField(label='Inciso', required=False)

    alinea = forms.CharField(label='Alínea', required=False)

    item = forms.CharField(label='Item', required=False)

    class Meta:
        model = LegislacaoCitada
        fields = ['tipo',
                  'numero',
                  'ano',
                  'disposicao',
                  'parte',
                  'livro',
                  'titulo',
                  'capitulo',
                  'secao',
                  'subsecao',
                  'artigo',
                  'paragrafo',
                  'inciso',
                  'alinea',
                  'item']

    def __init__(self, *args, **kwargs):

        row1 = crispy_layout_mixin.to_row(
            [('tipo', 4),
             ('numero', 4),
             ('ano', 4)])

        row2 = crispy_layout_mixin.to_row(
            [('disposicao', 3),
             ('parte', 3),
             ('livro', 3),
             ('titulo', 3)])

        row3 = crispy_layout_mixin.to_row(
            [('capitulo', 3),
             ('secao', 3),
             ('subsecao', 3),
             ('artigo', 3)])

        row4 = crispy_layout_mixin.to_row(
            [('paragrafo', 3),
             ('inciso', 3),
             ('alinea', 3),
             ('item', 3)])

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Fieldset(
                _('Incluir Legislação Citada'),
                row1, row2, row3, row4,
                form_actions()
            )
        )
        super(LegislacaoCitadaForm, self).__init__(*args, **kwargs)


class NumeracaoForm(ModelForm):

    class Meta:
        model = Numeracao
        fields = ['tipo_materia',
                  'numero_materia',
                  'ano_materia',
                  'data_materia']

    def __init__(self, excluir=False, *args, **kwargs):
        more = []
        if excluir:
            more = [Submit('Excluir', 'Excluir')]

        row1 = crispy_layout_mixin.to_row(
            [('tipo_materia', 12)])
        row2 = crispy_layout_mixin.to_row(
            [('numero_materia', 4), ('ano_materia', 4), ('data_materia', 4)])

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Incluir Numeração'),
                row1, row2,
                form_actions(more=more)
            )
        )
        super(NumeracaoForm, self).__init__(*args, **kwargs)


class DespachoInicialForm(ModelForm):

    class Meta:
        model = DespachoInicial
        fields = ['comissao']

    def __init__(self, excluir=False, *args, **kwargs):

        more = []
        if excluir:
            more = [Submit('Excluir', 'Excluir')]
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Adicionar Despacho Inicial'),
                'comissao',
                form_actions(more=more)
            )
        )
        super(DespachoInicialForm, self).__init__(*args, **kwargs)


class MateriaAnexadaForm(ModelForm):

    tipo = forms.ModelChoiceField(
        label='Tipo',
        required=True,
        queryset=TipoMateriaLegislativa.objects.all(),
        empty_label='Selecione',
    )

    numero = forms.CharField(label='Número', required=True)

    ano = forms.CharField(label='Ano', required=True)

    class Meta:
        model = Anexada
        fields = ['tipo', 'numero', 'ano',
                  'data_anexacao', 'data_desanexacao']
        widgets = {
            'data_anexacao': forms.DateInput(attrs={'class': 'dateinput'}),
            'data_desanexacao': forms.DateInput(attrs={'class': 'dateinput'}),
        }

    def __init__(self, excluir=False, *args, **kwargs):

        row1 = crispy_layout_mixin.to_row(
            [('tipo', 4), ('numero', 4), ('ano', 4)])
        row2 = crispy_layout_mixin.to_row(
            [('data_anexacao', 6), ('data_desanexacao', 6)])

        more = []
        if excluir:
            more = [Submit('Excluir', 'Excluir')]

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Anexar Matéria'),
                row1, row2,
                form_actions(more=more)
            )
        )
        super(MateriaAnexadaForm, self).__init__(
            *args, **kwargs)


class FormularioSimplificadoForm(ModelForm):

    class Meta:
        model = MateriaLegislativa
        fields = ['tipo',
                  'numero',
                  'ano',
                  'data_apresentacao',
                  'numero_protocolo',
                  'regime_tramitacao',
                  'em_tramitacao',
                  'ementa',
                  'texto_original']
        exclude = ['anexadas']
        widgets = {
            'data_apresentacao': forms.DateInput(attrs={'class': 'dateinput'}),
        }

    def clean_texto_original(self):
        texto_original = self.cleaned_data.get('texto_original', False)
        if texto_original:
            if texto_original.size > MAX_DOC_UPLOAD_SIZE:
                raise ValidationError("Arquivo muito grande. ( > 5mb )")
            return texto_original
        else:
            raise ValidationError("Não foi possível salvar o arquivo.")

    def __init__(self, *args, **kwargs):

        row1 = crispy_layout_mixin.to_row(
            [('tipo', 4),
             ('numero', 4),
             ('ano', 4)])

        row2 = crispy_layout_mixin.to_row(
            [('data_apresentacao', 4),
             ('numero_protocolo', 4),
             ('regime_tramitacao', 4)])

        row3 = crispy_layout_mixin.to_row(
            [('texto_original', 9),
             ('em_tramitacao', 3)])

        row4 = crispy_layout_mixin.to_row(
            [('ementa', 12)])

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Formulário Simplificado'),
                Fieldset(
                    _('Identificação Básica'),
                    row1, row2, row3, row4
                ),
                form_actions()
            )
        )
        super(FormularioSimplificadoForm, self).__init__(*args, **kwargs)


class FormularioCadastroForm(ModelForm):

    class Meta:
        model = MateriaLegislativa
        fields = ['tipo',
                  'numero',
                  'ano',
                  'data_apresentacao',
                  'numero_protocolo',
                  'tipo_apresentacao',
                  'texto_original',
                  'apelido',
                  'dias_prazo',
                  'polemica',
                  'objeto',
                  'regime_tramitacao',
                  'em_tramitacao',
                  'data_fim_prazo',
                  'data_publicacao',
                  'complementar',
                  'tipo_origem_externa',
                  'numero_origem_externa',
                  'ano_origem_externa',
                  'local_origem_externa',
                  'data_origem_externa',
                  'ementa',
                  'indexacao',
                  'observacao']

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Formulário de Cadastro'),
                Fieldset(
                    _('Identificação Básica'),
                    'tipo',
                    'numero',
                    'ano',
                    'data_apresentacao',
                    'numero_protocolo',
                    'tipo_apresentacao',
                    'texto_original'
                ),
                Fieldset(
                    _('Outras Informações'),
                    'apelido',
                    'dias_prazo',
                    'polemica',
                    'objeto',
                    'regime_tramitacao',
                    'em_tramitacao',
                    'data_fim_prazo',
                    'data_publicacao',
                    'complementar'
                ),
                Fieldset(
                    _('Origem Externa'),
                    'tipo_origem_externa',
                    'numero_origem_externa',
                    'ano_origem_externa',
                    'local_origem_externa',
                    'data_origem_externa'
                ),
                Fieldset(
                    _('Dados Textuais'),
                    'ementa',
                    'indexacao',
                    'observacao'
                ),
                form_actions()
            )
        )
        super(FormularioCadastroForm, self).__init__(*args, **kwargs)


class AutoriaForm(ModelForm):
    autor = forms.ModelChoiceField(
        label=_('Autor'),
        required=True,
        queryset=Autor.objects.all().order_by('tipo', 'nome'),
    )
    primeiro_autor = forms.ChoiceField(
        label=_('Primeiro Autor'),
        required=True,
        choices=[(True, _('Sim')), (False, _('Não'))],
    )

    class Meta:
        model = Autoria
        fields = ['autor',
                  'primeiro_autor',
                  'partido']

    def __init__(self, excluir=False, *args, **kwargs):

        row1 = crispy_layout_mixin.to_row(
            [('autor', 4), ('primeiro_autor', 4), ('partido', 4)])

        more = []
        if excluir:
            more = [Submit('Excluir', 'Excluir')]

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Adicionar Autoria'),
                row1,
                form_actions(more=more)
            )
        )
        super(AutoriaForm, self).__init__(
            *args, **kwargs)


class MateriaLegislativaPesquisaForm(ModelForm):

    autor = forms.CharField(widget=forms.HiddenInput(), required=False)

    localizacao = forms.ModelChoiceField(
        label='Localização Atual',
        required=False,
        queryset=UnidadeTramitacao.objects.all(),
        empty_label='Selecione',
    )

    situacao = forms.ModelChoiceField(
        label='Situação',
        required=False,
        queryset=StatusTramitacao.objects.all(),
        empty_label='Selecione',
    )

    em_tramitacao = forms.ChoiceField(required=False,
                                      label='Tramitando',
                                      choices=em_tramitacao(),
                                      widget=forms.Select(
                                        attrs={'class': 'selector'}))

    publicacao_inicial = forms.DateField(label=u'Data Publicação Inicial',
                                         input_formats=['%d/%m/%Y'],
                                         required=False,
                                         widget=forms.DateInput(
                                            format='%d/%m/%Y',
                                            attrs={'class': 'dateinput'}))

    publicacao_final = forms.DateField(label=u'Data Publicação Final',
                                       input_formats=['%d/%m/%Y'],
                                       required=False,
                                       widget=forms.DateInput(
                                            format='%d/%m/%Y',
                                            attrs={'class': 'dateinput'}))

    apresentacao_inicial = forms.DateField(label=u'Data Apresentação Inicial',
                                           input_formats=['%d/%m/%Y'],
                                           required=False,
                                           widget=forms.DateInput(
                                            format='%d/%m/%Y',
                                            attrs={'class': 'dateinput'}))

    apresentacao_final = forms.DateField(label=u'Data Apresentação Final',
                                         input_formats=['%d/%m/%Y'],
                                         required=False,
                                         widget=forms.DateInput(
                                            format='%d/%m/%Y',
                                            attrs={'class': 'dateinput'}))

    class Meta:
        model = MateriaLegislativa
        fields = ['tipo',
                  'numero',
                  'ano',
                  'numero_protocolo',
                  'apresentacao_inicial',
                  'apresentacao_final',
                  'publicacao_inicial',
                  'publicacao_final',
                  'autor',
                  'local_origem_externa',
                  'localizacao',
                  'em_tramitacao',
                  'situacao']

    def __init__(self, *args, **kwargs):

        row1 = crispy_layout_mixin.to_row(
            [('tipo', 12)])
        row2 = crispy_layout_mixin.to_row(
            [('numero', 4),
             ('ano', 4),
             ('numero_protocolo', 4)])
        row3 = crispy_layout_mixin.to_row(
            [('apresentacao_inicial', 6),
             ('apresentacao_final', 6)])
        row4 = crispy_layout_mixin.to_row(
            [('publicacao_inicial', 6),
             ('publicacao_final', 6)])
        row5 = crispy_layout_mixin.to_row(
                 [('autor', 0),
                  (Button('pesquisar',
                          'Pesquisar Autor',
                          css_class='btn btn-primary btn-sm'), 2),
                  (Button('limpar',
                          'limpar Autor',
                          css_class='btn btn-primary btn-sm'), 10)])
        row6 = crispy_layout_mixin.to_row(
            [('local_origem_externa', 6),
             ('localizacao', 6)])
        row7 = crispy_layout_mixin.to_row(
            [('em_tramitacao', 6),
             ('situacao', 6)])

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(_('Pesquisa Básica'),
                     row1, row2, row3, row4,
                     HTML(sapl.utils.autor_label),
                     HTML(sapl.utils.autor_modal),
                     row5, row6, row7,
                     form_actions(save_label='Pesquisar'))
        )
        super(MateriaLegislativaPesquisaForm, self).__init__(
            *args, **kwargs)
