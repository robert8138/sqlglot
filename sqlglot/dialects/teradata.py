from __future__ import annotations

from sqlglot import exp, generator, parser, tokens
from sqlglot.dialects.dialect import Dialect
from sqlglot.tokens import TokenType


class Teradata(Dialect):
    class Tokenizer(tokens.Tokenizer):
        # https://docs.teradata.com/r/Teradata-Database-SQL-Functions-Operators-Expressions-and-Predicates/March-2017/Comparison-Operators-and-Functions/Comparison-Operators/ANSI-Compliance
        KEYWORDS = {
            **tokens.Tokenizer.KEYWORDS,
            "BYTEINT": TokenType.SMALLINT,
            "SEL": TokenType.SELECT,
            "INS": TokenType.INSERT,
            "MOD": TokenType.MOD,
            "LT": TokenType.LT,
            "LE": TokenType.LTE,
            "GT": TokenType.GT,
            "GE": TokenType.GTE,
            "^=": TokenType.NEQ,
            "NE": TokenType.NEQ,
            "NOT=": TokenType.NEQ,
        }

        # teradata does not support % for modulus
        SINGLE_TOKENS = {**tokens.Tokenizer.SINGLE_TOKENS}
        SINGLE_TOKENS.pop("%")

    class Parser(parser.Parser):
        CHARSET_TRANSLATORS = {
            "GRAPHIC_TO_KANJISJIS",
            "GRAPHIC_TO_LATIN",
            "GRAPHIC_TO_UNICODE",
            "GRAPHIC_TO_UNICODE_PadSpace",
            "KANJI1_KanjiEBCDIC_TO_UNICODE",
            "KANJI1_KanjiEUC_TO_UNICODE",
            "KANJI1_KANJISJIS_TO_UNICODE",
            "KANJI1_SBC_TO_UNICODE",
            "KANJISJIS_TO_GRAPHIC",
            "KANJISJIS_TO_LATIN",
            "KANJISJIS_TO_UNICODE",
            "LATIN_TO_GRAPHIC",
            "LATIN_TO_KANJISJIS",
            "LATIN_TO_UNICODE",
            "LOCALE_TO_UNICODE",
            "UNICODE_TO_GRAPHIC",
            "UNICODE_TO_GRAPHIC_PadGraphic",
            "UNICODE_TO_GRAPHIC_VarGraphic",
            "UNICODE_TO_KANJI1_KanjiEBCDIC",
            "UNICODE_TO_KANJI1_KanjiEUC",
            "UNICODE_TO_KANJI1_KANJISJIS",
            "UNICODE_TO_KANJI1_SBC",
            "UNICODE_TO_KANJISJIS",
            "UNICODE_TO_LATIN",
            "UNICODE_TO_LOCALE",
            "UNICODE_TO_UNICODE_FoldSpace",
            "UNICODE_TO_UNICODE_Fullwidth",
            "UNICODE_TO_UNICODE_Halfwidth",
            "UNICODE_TO_UNICODE_NFC",
            "UNICODE_TO_UNICODE_NFD",
            "UNICODE_TO_UNICODE_NFKC",
            "UNICODE_TO_UNICODE_NFKD",
        }

        FUNC_TOKENS = {*parser.Parser.FUNC_TOKENS}
        FUNC_TOKENS.remove(TokenType.REPLACE)

        STATEMENT_PARSERS = {
            **parser.Parser.STATEMENT_PARSERS,  # type: ignore
            TokenType.REPLACE: lambda self: self._parse_create(),
        }

        FUNCTION_PARSERS = {
            **parser.Parser.FUNCTION_PARSERS,  # type: ignore
            "TRANSLATE": lambda self: self._parse_translate(self.STRICT_CAST),
        }

        def _parse_translate(self, strict: bool) -> exp.Expression:
            this = self._parse_conjunction()

            if not self._match(TokenType.USING):
                self.raise_error("Expected USING in TRANSLATE")

            if self._match_texts(self.CHARSET_TRANSLATORS):
                charset_split = self._prev.text.split("_TO_")
                to = self.expression(exp.CharacterSet, this=charset_split[1])
            else:
                self.raise_error("Expected a character set translator after USING in TRANSLATE")

            return self.expression(exp.Cast if strict else exp.TryCast, this=this, to=to)

        # FROM before SET in Teradata UPDATE syntax
        # https://docs.teradata.com/r/Enterprise_IntelliFlex_VMware/Teradata-VantageTM-SQL-Data-Manipulation-Language-17.20/Statement-Syntax/UPDATE/UPDATE-Syntax-Basic-Form-FROM-Clause
        def _parse_update(self) -> exp.Expression:
            return self.expression(
                exp.Update,
                **{  # type: ignore
                    "this": self._parse_table(alias_tokens=self.UPDATE_ALIAS_TOKENS),
                    "from": self._parse_from(),
                    "expressions": self._match(TokenType.SET)
                    and self._parse_csv(self._parse_equality),
                    "where": self._parse_where(),
                },
            )

    class Generator(generator.Generator):
        PROPERTIES_LOCATION = {
            **generator.Generator.PROPERTIES_LOCATION,  # type: ignore
            exp.PartitionedByProperty: exp.Properties.Location.POST_INDEX,
        }

        def partitionedbyproperty_sql(self, expression: exp.PartitionedByProperty) -> str:
            return f"PARTITION BY {self.sql(expression, 'this')}"

        # FROM before SET in Teradata UPDATE syntax
        # https://docs.teradata.com/r/Enterprise_IntelliFlex_VMware/Teradata-VantageTM-SQL-Data-Manipulation-Language-17.20/Statement-Syntax/UPDATE/UPDATE-Syntax-Basic-Form-FROM-Clause
        def update_sql(self, expression: exp.Update) -> str:
            this = self.sql(expression, "this")
            from_sql = self.sql(expression, "from")
            set_sql = self.expressions(expression, flat=True)
            where_sql = self.sql(expression, "where")
            sql = f"UPDATE {this}{from_sql} SET {set_sql}{where_sql}"
            return self.prepend_ctes(expression, sql)

        def mod_sql(self, expression: exp.Mod) -> str:
            return self.binary(expression, "MOD")
