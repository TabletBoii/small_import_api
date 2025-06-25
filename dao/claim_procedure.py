import asyncio
from typing import Optional, Tuple, List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


join_list = {
    "cd": "join claim_detail cd on cd.claim = c.inc",
    "ccr": "join #cca_result ccr on c.inc = ccr.claim",
    "ccur": "join currency ccur on c.currencyclaim = ccur.inc",
    "t": "join tour t on t.inc = c.tour",
    "tw": "left join town tw on t.town = tw.inc",
    "st": "join state st on t.state = st.inc",
    "stf": "join state stf on t.stateFrom = stf.inc",
    "p": "join partner p on c.partner = p.inc",
    "[ow]": "join partner [ow] on c.[owner] = [ow].inc",
    "ptw": "left join town ptw on p.town = ptw.inc",
    "pt": "left join parttype pt on p.parttype = pt.inc",
    "ss": "outer apply (select top 1 employee from supervisor s where s.partner = c.partner) ss",
    "sup": "left join usnames sup on sup.code = ss.employee",
    "vc": "join v_claim_confirmed_title vc on c.confirmed_full = vc.inc",
    "us": "left join usnames us on [us].code = c.[user]",
    "ctype": "left join ctype on c.ctype = ctype.inc",
    "r": "left join route r on r.tour = t.inc and r.routeindex = 1",
    "dept": "left join town dept on r.town = dept.inc",
    "deps": "left join state deps on deps.inc = dept.state",
    "tt": "left join tourtype tt on tt.inc = t.tourtype ",
    "spog": "left join spog on c.spog = spog.inc",
    "ptype": "left join ptype on spog.ptype = ptype.inc",
    "stw": "left join state stw on stw.inc = ptw.state"
}

field_to_join_dict = {

}

alias_field_dict = {
    "claim$inc": "c.inc",
    "claim$status": "c.status",
    "claim$paidstatus": """case 
        when c.status = 1 then 'Оплачена'
        when c.status = 2 and c.partpayment = 1 then 'Частично оплачена'
        when c.status = 2 and c.partpayment = 0 then 'Не оплачена'        
        when c.status = 3 then 'Отменена'
        end claim$paidstatus
    """,
    "partner$inc": "p.inc",
    "partner$name": "p.name",
    "partner$adate": "p.adate",
    "partner$internet": "p.internet",
    "partner$phone": "p.phones",
    "partner$state": "stw.name",
    "partner$town$inc": "ptw.inc",
    "partner$town$name": "ptw.name",
    "tour$name": "t.name",
    "claim$rdate": "c.rdate",
    "claim$cdate": "c.cdate",
    "claim$cdatetime": "c.cdatetime",
    "claim$datebeg": "c.datebeg",
    "claim$dateend": "c.dateend",
    "claim$nights": "c.nights",
    "claim$confirmeddate": "c.confirmeddate",
    "claim$net": "ccr.net",
    "claim$anet": "ccr.anet",
    "claim$paidnet": "ccr.paidnet",
    "claim$debtnet": "ccr.debtnet",
    "claim$cost": "ccr.cost",
    "claim$paidcost": "ccr.paidcost",
    "claim$debtcost": "ccr.debtcost",
    "claim$clientcost": "ccr.clientcost",
    "claim$clientdebt": "ccr.clientdebt",
    "claim$mediatorsum": "ccr.mediatorsum",
    "claim$fixcommiss": "ccr.fixcommiss",
    "claim$commiss": "ccr.commiss",
    "claim$earlycommiss": "ccr.earlycommiss",
    "claim$discount": "ccr.discount",
    "claim$discommiss": "ccr.discommiss",
    "claim$supplement": "ccr.supplement",
    "claim$suppcommiss": "ccr.suppcommiss",
    "claim$common_commiss": "ccr.common_commiss",
    "claim$total_commiss": "ccr.total_commiss",
    "claim$tax": "ccr.tax",
    "claim$amount_to_pay": "ccr.amount_to_pay",
    "claim$kickback": "ccr.kickback",
    "claim$profit": "ccr.profit",
    "claim$aprofit": "ccr.aprofit",
    "claim$cost_with_commiss": "ccr.cost_with_commiss",
    "claim$precision": "ccr.precision",
    "claim$currency$alias": "ccur.alias",
    "claim$note": "cd.note",
    "claim$comment": "cd.comment",
    "claim$privatecomment": "cd.privatecomment",
    "claim$partnercomment": "cd.partnercomment",
    "partner$parttype$name": "pt.name",
    "current$date": "getdate() current$date",
    "tilldate$begin": "CAST(DATEDIFF(DAY, GETDATE(), c.datebeg) AS INT) tilldate$begin",
    "supervisor$inc": "ss.employee",
    "supervisor$name": "sup.name",
    "town$inc": "tw.inc",
    "town$name": "tw.name",
    "confimredstatus$inc": "vc.inc",
    "confimredstatus$name": "vc.name",
    "user$name": "us.name",
    "commission$percent": "c.commission",
    "ctype$inc": "c.ctype",
    "ctype$name": "ctype.name",
    "state$inc": "st.inc",
    "state$name": "st.name",
    "statefrom$inc": "stf.inc",
    "statefrom$name": "stf.name",
    "adl_count": "(select count(*) from people p where p.claim = c.inc and p.human in ('MR', 'MRS')) adl_count",
    "chd_count": "(select count(*) from people p where p.claim = c.inc and p.human in ('CHD')) chd_count",
    "all_pax": "(select count(*) from people p where p.claim = c.inc and p.human in ('MR', 'MRS', 'CHD')) all_pax",
    "departure$town$inc": "dept.inc",
    "departure$town$name": "dept.name",
    "departure$state$inc": "deps.inc",
    "departure$state$name": "deps.name",
    "tourtype$inc": "tt.inc",
    "tourtype$name": "tt.name",
    "ptype$inc": "ptype.inc",
    "ptype$name": "ptype.name"
}

title_alias_dict = {
    "Заявка №": "claim$inc",
    "Статус заявки": "claim$paidstatus",
    "Код заказчика": "partner$inc",
    "Заказчик": "partner$name",
    "Дата добавления партнёра": "partner$adate",
    "Веб-сайт партнёра": "partner$internet",
    "Телефоны заказчика": "partner$phone",
    "Страна партнёра": "partner$state",
    "ID города партнёра": "partner$town$inc",
    "Город партнёра": "partner$town$name",
    "Тур": "tour$name",
    "Дата создания заявки": "claim$rdate",
    "Дата расчёта заявки": "claim$cdate",
    "Дата/время расчёта заявки": "claim$cdatetime",
    "Дата начала тура": "claim$datebeg",
    "Дата окончания тура": "claim$dateend",
    "Ночей": "claim$nights",
    "Дата подтверждения/неподтверждения": "claim$confirmeddate",
    "Нетто-сумма": "claim$net",
    "Агентское нетто (?)": "claim$anet",
    "Оплачено (нетто)": "claim$paidnet",
    "Долг (нетто)": "claim$debtnet",
    "По каталогу": "claim$cost",
    "Оплачено": "claim$paidcost",
    "Долг": "claim$debtcost",
    "Стоимость для клиента": "claim$clientcost",
    "Долг клиента": "claim$clientdebt",
    "Сумма посредника": "claim$mediatorsum",
    "Фиксированная комиссия": "claim$fixcommiss",
    "Комиссия": "claim$commiss",
    "Ранняя комиссия": "claim$earlycommiss",
    "Скидка": "claim$discount",
    "Скидка комиссии": "claim$discommiss",
    "Доплата": "claim$supplement",
    "Дополнительная комиссия": "claim$suppcommiss",
    "Общая комиссия": "claim$common_commiss",
    "Сумма комиссии": "claim$total_commiss",
    "Налог": "claim$tax",
    "К оплате": "claim$amount_to_pay",
    "Бонус": "claim$kickback",
    "Прибыль": "claim$profit",
    "Агентская прибыль (?)": "claim$aprofit",
    "Стоимость с комиссией": "claim$cost_with_commiss",
    "Точность расчёта": "claim$precision",
    "$": "claim$currency$alias",
    "Заметка": "claim$note",
    "Комментарий": "claim$comment",
    "Внутреннее примечание": "claim$privatecomment",
    "Комментарий партнёра": "claim$partnercomment",
    "Тип партнёра": "partner$parttype$name",
    "Текущая дата": "current$date",
    "Дней до начала тура": "tilldate$begin",
    "ID куратора": "supervisor$inc",
    "Куратор": "supervisor$name",
    "ID города": "town$inc",
    "Город": "town$name",
    "ID статуса подтверждения": "confimredstatus$inc",
    "Подтверждение": "confimredstatus$name",
    "Пользователь": "user$name",
    "Комиссия (%)": "commission$percent",
    "ID типа заявки": "ctype$inc",
    "Тип заявки": "ctype$name",
    "ID основной страны пребывания": "state$inc",
    "Основная страна пребывания": "state$name",
    "ID исходного состояния": "statefrom$inc",
    "Исходное состояние": "statefrom$name",
    "Взрослых": "adl_count",
    "Детей": "chd_count",
    "Всего пассажиров": "all_pax",
    "ID города вылета": "departure$town$inc",
    "Город вылета": "departure$town$name",
    "ID типа тура": "tourtype$inc",
    "Тур: Вид тура": "tourtype$name",
    "ID типа пакета": "ptype$inc",
    "Тип пакета": "ptype$name"
}

joins_path = {
    "cd": None,
    "ccr": None,
    "ccur": None,
    "t": None,
    "tw": "t",
    "st": "t",
    "stf": "t",
    "p": None,
    "[ow]": None,
    "ptw": "p",
    "pt": "p",
    "ss": None,
    "sup": "ss",
    "vc": None,
    "us": None,
    "ctype": None,
    "r": "t",
    "dept": "r",
    "deps": "dept",
    "tt": "t",
    "spog": None,
    "ptype": "spog",
    "stw": "ptw"
}


class ClaimProcedure:
    def __init__(
            self,
            session: AsyncSession,
            claim_inc: Optional[int] = None,
            date_begin_tuple: Optional[Tuple[str, str]] = None,
            claim_create_date_tuple: Optional[Tuple[str, str]] = None,
            confirm_date_tuple: Optional[Tuple[str, str]] = None,
            r_date_tuple: Optional[Tuple[str, str]] = None,
            selected_fields_list: Optional[List[str]] = None
    ):
        self.session = session
        self.claim_inc = claim_inc
        self.date_begin_tuple = date_begin_tuple
        self.claim_create_date_tuple = claim_create_date_tuple
        self.confirm_date_tuple = confirm_date_tuple
        self.r_date_tuple = r_date_tuple
        self.selected_fields_list = selected_fields_list
        self.date_tuple_list = {
            "date_begin_tuple": self.date_begin_tuple,
            "claim_create_date_tuple": self.claim_create_date_tuple,
            "confirm_date_tuple": self.confirm_date_tuple,
            "r_date_tuple": self.r_date_tuple
        }

    async def is_other_dates_not_empty(self, date_tuple_name: str | None) -> bool:
        for key, value in self.date_tuple_list.items():
            if date_tuple_name != key:
                if self.date_tuple_list[key] is not None:
                    self.date_tuple_list.pop(date_tuple_name)
                    return True
        return False

    async def create_cca_claim_temp_table(self):
        stmt = text(
            """
                create table #cca_claim (dummy int); 
                exec [Utils].CreateTempTableByType @p_type_name = 'cca_claim_table_type', @p_table = '#cca_claim'
            """
        )
        await self.session.execute(stmt)

    async def create_cca_result_temp_table(self):
        stmt = text(
            """
                create table #cca_result(dummy int)
                exec [Utils].CreateTempTableByType @p_type_name = 'cca_result_table_type', @p_table = '#cca_result'
            """
        )
        await self.session.execute(stmt)

    async def insert_into_cca_claim(self):
        stmt = text(
            f"""
                insert into #cca_claim (inc)
                select c.inc
                from claim c
                where
                    {f"{self.claim_inc} = c.inc and" if self.claim_inc is not None else ""}
                  
                    {f"c.datebeg between '{self.date_begin_tuple[0].replace("-", "")}' and '{self.date_begin_tuple[1].replace("-", "")}' {"and" if await self.is_other_dates_not_empty("date_begin_tuple") else ""}" if self.date_begin_tuple is not None else ""} 
                    
                    {f"c.cdate between '{self.claim_create_date_tuple[0].replace("-", "")}' and '{self.claim_create_date_tuple[1].replace("-", "")}' {'and' if await self.is_other_dates_not_empty("claim_create_date_tuple") else ""}" if self.claim_create_date_tuple is not None else ""}
                    
                    {f"c.confirmeddate between '{self.confirm_date_tuple[0].replace("-", "")}' and '{self.confirm_date_tuple[1].replace("-", "")}' {'and' if await self.is_other_dates_not_empty("confirm_date_tuple") else ""}" if self.confirm_date_tuple is not None else ""}
                    
                    {f"c.rdate between '{self.r_date_tuple[0].replace("-", "")}' and '{self.r_date_tuple[1].replace("-", "")}'" if self.r_date_tuple is not None else ""}
            """
        )
        print(stmt)
        await self.session.execute(stmt)

    async def exec_amount_calculation(self):
        stmt = text(
            """
                exec [up_Claims_CalculateAmounts]
            """
        )
        await self.session.execute(stmt)

    def is_join_duplicate(self, join_collection: list, join: str) -> bool:
        for element in join_collection:
            if element == join:
                return False
        return True

    def generate_main_select(self):
        query_field_str = ""
        query_join_str = ""
        translated_fields_list = [title_alias_dict[field] for field in self.selected_fields_list]
        query_field_list: List[str] = [alias_field_dict[field] for field in translated_fields_list]
        query_join_list = []
        for index, field in enumerate(query_field_list):
            tmp_join_sequence = []
            if index == len(query_field_list) - 1:
                query_field_str += f"{field}"
            else:
                query_field_str += f"{field}, "
            field_prefix = field.split(".")[0]

            if joins_path.get(field_prefix, "") == "":

                continue

            while True:
                if joins_path[field_prefix] is not None:
                    tmp_join_sequence.insert(0, field_prefix)
                    field_prefix = joins_path[field_prefix]
                else:
                    tmp_join_sequence.insert(0, field_prefix)
                    break
            for join in tmp_join_sequence:
                if self.is_join_duplicate(query_join_list, join):
                    query_join_list.append(join)

        for index, join in enumerate(query_join_list):
            if index == len(query_join_list) - 1:
                query_join_str += f"{join_list[join]}"
            else:
                query_join_str += f"{join_list[join]} "
        print(query_join_str)
        return f"""select {query_field_str} from claim c {query_join_str}"""

    async def execute_procedure_select(self):
        stmt_str = self.generate_main_select()
        print(stmt_str)
        stmt = text(
            stmt_str
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def drop_cca_claim_temp_table(self):
        stmt = text(
            """
                drop table #cca_claim
            """
        )
        await self.session.execute(stmt)

    async def drop_cca_result_temp_table(self):
        stmt = text(
            """
                drop table #cca_result
            """
        )
        await self.session.execute(stmt)

    async def get_claims(self):
        await self.create_cca_claim_temp_table()
        await self.create_cca_result_temp_table()
        await self.insert_into_cca_claim()
        await self.exec_amount_calculation()
        result = await self.execute_procedure_select()
        await self.drop_cca_claim_temp_table()
        await self.drop_cca_result_temp_table()
        return result


class MockSession:
    async def execute(self, string):
        ...


if __name__ == "__main__":
    inst = ClaimProcedure(
        session=MockSession(),
        cdate_tuple=("20240101", "20241231"),
        confirmdate_tuple=("20240101", "20241231"),
        rdate_tuple=("20240101", "20241231"),
        selected_fields_list=[
            "Страна партнёра",
            "ID заявки",
            "ID партнёра",
            "Название тура",
            "Агентское нетто (?)",
            "Город вылета",
            "ID региона вылета",
            "Регион вылета"
        ]
    )

    asyncio.run(inst.get_claims())
