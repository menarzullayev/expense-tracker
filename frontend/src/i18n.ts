export type Language = "uz" | "ru" | "en";

const STORAGE_KEY = "expense_tracker_language";
let current: Language = (localStorage.getItem(STORAGE_KEY) as Language | null) ?? "uz";

const translations: Record<Language, Record<string, string>> = {
  uz: {
    "Expense Tracker":"Xarajatlar nazorati","Secure & Private":"Xavfsiz va maxfiy","Take control of":"Moliyangizni","your":"o‘z","finances":"nazorat qiling",
    "Track expenses, manage budgets, and build better financial habits with a simple and powerful tool.":"Xarajatlarni kuzating, budjetlarni boshqaring va qulay hamda kuchli vosita bilan moliyaviy odatlaringizni yaxshilang.",
    "Track Expenses":"Xarajatlarni kuzatish","See where your money goes":"Pulingiz qayerga sarflanishini ko‘ring","Visual Insights":"Vizual tahlil","Understand your spending":"Xarajatlaringizni tushuning","Stay in Control":"Nazoratni saqlang","Build better financial habits":"Yaxshi moliyaviy odatlar yarating",
    "Welcome back":"Xush kelibsiz","Sign in to your account to continue":"Davom etish uchun hisobingizga kiring","Email address":"Email manzili","Password":"Parol","Remember me":"Meni eslab qol","Forgot password?":"Parolni unutdingizmi?","Sign in":"Kirish",
    "MAIN MENU":"ASOSIY MENYU","Dashboard":"Boshqaruv paneli","Transactions":"Tranzaksiyalar","Categories":"Kategoriyalar","Budgets":"Budjetlar","Reports":"Hisobotlar","SETTINGS":"SOZLAMALAR","Preferences":"Sozlamalar",
    "Search transactions, categories...":"Tranzaksiyalar, kategoriyalarni qidirish...","Total Expenses":"Jami xarajatlar","Total Income":"Jami daromad","Net Balance":"Sof balans","This month":"Shu oy","Cash flow":"Pul oqimi",
    "Expenses Overview":"Xarajatlar ko‘rinishi","Last 6 months":"Oxirgi 6 oy","Expenses by Category":"Kategoriyalar bo‘yicha xarajatlar","Recent Transactions":"So‘nggi tranzaksiyalar","Your latest activity":"So‘nggi faoliyatingiz","View all →":"Barchasini ko‘rish →","Budget Progress":"Budjet holati","Category spending":"Kategoriya xarajatlari","Spending category":"Xarajat kategoriyasi",
    "Add Expense":"Xarajat qo‘shish","Add Transaction":"Tranzaksiya qo‘shish","Here's an overview of your finances this month.":"Bu oygi moliyaviy holatingizning umumiy ko‘rinishi.","This module will use the same production API and data model.":"Ushbu modul ham bir xil production API va ma’lumotlar modelidan foydalanadi.","Manage your financial information.":"Moliyaviy ma’lumotlaringizni boshqaring.",
    "Transaction management":"Tranzaksiyalar boshqaruvi","Category management":"Kategoriyalar boshqaruvi","Budget management":"Budjet boshqaruvi","Financial reports":"Moliyaviy hisobotlar","No transactions found.":"Tranzaksiyalar topilmadi.","No categorized expenses yet.":"Kategoriyalangan xarajatlar hali yo‘q.","Add categories and transactions to track budgets.":"Budjetlarni kuzatish uchun kategoriyalar va tranzaksiyalar qo‘shing.",
    "NEW TRANSACTION":"YANGI TRANZAKSIYA","Expense":"Xarajat","Income":"Daromad","Amount":"Summa","Description":"Izoh","e.g. Grocery shopping":"masalan, oziq-ovqat xaridi","Account":"Hisob","Category":"Kategoriya","None":"Yo‘q","Date":"Sana","Save Transaction":"Tranzaksiyani saqlash","Create an account first.":"Avval hisob yarating.","Untitled":"Nomsiz","Uncategorized":"Kategoriyasiz","Home":"Bosh sahifa","Add":"Qo‘shish","Request failed":"So‘rov bajarilmadi","Invalid credentials":"Login yoki parol noto‘g‘ri"
  },
  ru: {
    "Expense Tracker":"Учет расходов","Secure & Private":"Безопасно и конфиденциально","Take control of":"Возьмите под контроль","your":"свои","finances":"финансы",
    "Track expenses, manage budgets, and build better financial habits with a simple and powerful tool.":"Отслеживайте расходы, управляйте бюджетами и формируйте полезные финансовые привычки с помощью простого и мощного инструмента.",
    "Track Expenses":"Учет расходов","See where your money goes":"Смотрите, куда уходят ваши деньги","Visual Insights":"Визуальная аналитика","Understand your spending":"Понимайте свои расходы","Stay in Control":"Сохраняйте контроль","Build better financial habits":"Формируйте полезные финансовые привычки",
    "Welcome back":"С возвращением","Sign in to your account to continue":"Войдите в аккаунт, чтобы продолжить","Email address":"Email","Password":"Пароль","Remember me":"Запомнить меня","Forgot password?":"Забыли пароль?","Sign in":"Войти",
    "MAIN MENU":"ГЛАВНОЕ МЕНЮ","Dashboard":"Панель управления","Transactions":"Транзакции","Categories":"Категории","Budgets":"Бюджеты","Reports":"Отчеты","SETTINGS":"НАСТРОЙКИ","Preferences":"Настройки",
    "Search transactions, categories...":"Поиск транзакций, категорий...","Total Expenses":"Всего расходов","Total Income":"Всего доходов","Net Balance":"Чистый баланс","This month":"В этом месяце","Cash flow":"Денежный поток",
    "Expenses Overview":"Обзор расходов","Last 6 months":"Последние 6 месяцев","Expenses by Category":"Расходы по категориям","Recent Transactions":"Последние транзакции","Your latest activity":"Ваша последняя активность","View all →":"Показать все →","Budget Progress":"Состояние бюджета","Category spending":"Расходы по категориям","Spending category":"Категория расходов",
    "Add Expense":"Добавить расход","Add Transaction":"Добавить транзакцию","Here's an overview of your finances this month.":"Обзор ваших финансов за этот месяц.","This module will use the same production API and data model.":"Этот модуль будет использовать тот же production API и модель данных.","Manage your financial information.":"Управляйте финансовой информацией.",
    "Transaction management":"Управление транзакциями","Category management":"Управление категориями","Budget management":"Управление бюджетом","Financial reports":"Финансовые отчеты","No transactions found.":"Транзакции не найдены.","No categorized expenses yet.":"Категоризированных расходов пока нет.","Add categories and transactions to track budgets.":"Добавьте категории и транзакции для отслеживания бюджета.",
    "NEW TRANSACTION":"НОВАЯ ТРАНЗАКЦИЯ","Expense":"Расход","Income":"Доход","Amount":"Сумма","Description":"Описание","e.g. Grocery shopping":"например, покупки продуктов","Account":"Счет","Category":"Категория","None":"Нет","Date":"Дата","Save Transaction":"Сохранить транзакцию","Create an account first.":"Сначала создайте счет.","Untitled":"Без названия","Uncategorized":"Без категории","Home":"Главная","Add":"Добавить","Request failed":"Не удалось выполнить запрос","Invalid credentials":"Неверный логин или пароль"
  },
  en: {}
};

export function language(): Language { return current; }
export function locale(): string { return current === "uz" ? "uz-UZ" : current === "ru" ? "ru-RU" : "en-US"; }
export function setLanguage(next: Language): void { current = next; localStorage.setItem(STORAGE_KEY, next); document.documentElement.lang = next; }
export function t(value: string): string { return translations[current][value] ?? value; }
export function languageSwitcher(): string {
  return `<div class="language-switcher" role="group" aria-label="Language">
    <button type="button" data-language="uz" class="${current==="uz"?"active":""}">UZ</button>
    <button type="button" data-language="ru" class="${current==="ru"?"active":""}">RU</button>
    <button type="button" data-language="en" class="${current==="en"?"active":""}">EN</button>
  </div>`;
}
export function localize(root: ParentNode = document): void {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const nodes: Text[] = [];
  let node: Node | null;
  while ((node = walker.nextNode())) nodes.push(node as Text);
  for (const text of nodes) {
    const value = text.nodeValue ?? "";
    const trimmed = value.trim();
    if (!trimmed) continue;
    const translated = t(trimmed);
    if (translated !== trimmed) text.nodeValue = value.replace(trimmed, translated);
  }
  root.querySelectorAll<HTMLInputElement | HTMLTextAreaElement>("input, textarea").forEach(el => {
    const placeholder = el.getAttribute("placeholder");
    if (placeholder) el.setAttribute("placeholder", t(placeholder));
  });
  document.documentElement.lang = current;
}
export function bindLanguageSwitcher(onChange: () => void): void {
  document.querySelectorAll<HTMLButtonElement>("[data-language]").forEach(button => button.addEventListener("click", () => {
    const next = button.dataset.language as Language;
    if (next && next !== current) { setLanguage(next); onChange(); }
  }));
}
