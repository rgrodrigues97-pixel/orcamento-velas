from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ProdutoCatalogo:
    id: int
    nome: str
    valor_mao_de_obra: float  # Preço da MO por unidade (R$)
    cera_kg_unitario: float   # Consumo de cera por vela (em kg)
    pavio_m_unitario: float   # Consumo de pavio por vela (em metros)


# Catálogo base inicial com modelos comuns de velas
CATALOGO: List[ProdutoCatalogo] = [
    ProdutoCatalogo(
        id=1,
        nome="Vela Cilíndrica Pequena (100g)",
        valor_mao_de_obra=4.50,
        cera_kg_unitario=0.100,
        pavio_m_unitario=0.12,
    ),
    ProdutoCatalogo(
        id=2,
        nome="Vela Cilíndrica Média (180g)",
        valor_mao_de_obra=6.50,
        cera_kg_unitario=0.180,
        pavio_m_unitario=0.15,
    ),
    ProdutoCatalogo(
        id=3,
        nome="Vela Pote de Vidro (200g)",
        valor_mao_de_obra=8.00,
        cera_kg_unitario=0.200,
        pavio_m_unitario=0.16,
    ),
    ProdutoCatalogo(
        id=4,
        nome="Vela Decorativa Esculpida (350g)",
        valor_mao_de_obra=12.00,
        cera_kg_unitario=0.350,
        pavio_m_unitario=0.22,
    ),
]


@dataclass
class ItemOrcamento:
    produto: ProdutoCatalogo
    quantidade: int

    @property
    def subtotal_mo(self) -> float:
        return round(self.quantidade * self.produto.valor_mao_de_obra, 2)

    @property
    def total_cera_kg(self) -> float:
        return round(self.quantidade * self.produto.cera_kg_unitario, 3)

    @property
    def total_pavio_m(self) -> float:
        return round(self.quantidade * self.produto.pavio_m_unitario, 2)


@dataclass
class Orcamento:
    cliente_nome: str
    cliente_contato: str
    data_emissao: str
    numero_orcamento: str
    itens: List[ItemOrcamento]
    preco_kg_cera: float = 38.00     # Preço de referência da cera (R$/kg)
    preco_metro_pavio: float = 0.80  # Preço de referência do pavio (R$/m)
    desconto_mo: float = 0.00        # Desconto em R$ na mão de obra
    observacoes: Optional[str] = ""

    # Totais de Mão de Obra (Cobrança do Serviço)
    @property
    def total_mo_bruto(self) -> float:
        return round(sum(item.subtotal_mo for item in self.itens), 2)

    @property
    def total_mo_liquido(self) -> float:
        total = self.total_mo_bruto - self.desconto_mo
        return round(max(total, 0.0), 2)

    # Totais Físicos de Insumos (Material a ser fornecido pelo cliente)
    @property
    def total_cera_kg(self) -> float:
        return round(sum(item.total_cera_kg for item in self.itens), 3)

    @property
    def total_pavio_m(self) -> float:
        return round(sum(item.total_pavio_m for item in self.itens), 2)

    # Custos Estimados dos Insumos Fornecidos
    @property
    def custo_estimado_cera(self) -> float:
        return round(self.total_cera_kg * self.preco_kg_cera, 2)

    @property
    def custo_estimado_pavio(self) -> float:
        return round(self.total_pavio_m * self.preco_metro_pavio, 2)

    @property
    def custo_total_insumos(self) -> float:
        return round(self.custo_estimado_cera + self.custo_estimado_pavio, 2)

    # Custo Global de Referência (Serviço + Materiais)
    @property
    def valor_global_producao(self) -> float:
        return round(self.total_mo_liquido + self.custo_total_insumos, 2)