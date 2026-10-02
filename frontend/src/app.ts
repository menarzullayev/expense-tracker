const API = (window as Window & { ENV_API?: string }).ENV_API ?? "http://localhost:8000";
const tokenKey = "expense_tracker_token";
const state = { token: localStorage.getItem(tokenKey) ?? "", accounts: [] as any[], categories: [] as any[] };

async function api(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (state.token) headers.set("Authorization", `Bearer ${state.token}`);
  const res = await fetch(`${API}${path}`, { ...init, headers });
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail ?? `HTTP ${res.status}`);
  return res.status === 204 ? null : res.json();
}

function renderLogin() {
  document.querySelector<HTMLDivElement>("#app")!.innerHTML = `
  <main class="shell auth"><section class="card"><h1>Expense Tracker</h1><p class="muted">Private, auditable personal finance.</p>
  <form id="login"><label>Email<input name="email" type="email" required value="demo@example.com"></label>
  <label>Password<input name="password" type="password" required value="StrongPass123!"></label><button>Sign in</button></form>
  <button id="register" class="secondary">Create account</button><p id="error" class="error"></p></section></main>`;
  document.querySelector("#login")!.addEventListener("submit", async (e) => { e.preventDefault(); const f = new FormData(e.currentTarget as HTMLFormElement);
    try { const r = await api("/v1/auth/login", { method:"POST", body: JSON.stringify({email:f.get("email"), password:f.get("password")}) }); state.token=r.access_token; localStorage.setItem(tokenKey,state.token); renderApp(); } catch(err) { (document.querySelector("#error") as HTMLElement).textContent=String(err); }
  });
  document.querySelector("#register")!.addEventListener("click", async () => { const email=prompt("Email"); const password=prompt("Password (10+ chars)"); const display_name=prompt("Name"); if(!email||!password||!display_name)return;
    try { const r=await api("/v1/auth/register",{method:"POST",body:JSON.stringify({email,password,display_name,base_currency:"UZS"})}); state.token=r.access_token; localStorage.setItem(tokenKey,state.token); renderApp(); } catch(err){ alert(String(err)); }
  });
}

function money(v: unknown) { return new Intl.NumberFormat("uz-UZ", { maximumFractionDigits: 0 }).format(Number(v)); }

async function renderApp() {
  try { const [me, accounts, categories, summary, txs] = await Promise.all([api("/v1/auth/me"),api("/v1/finance/accounts"),api("/v1/finance/categories"),api("/v1/finance/summary"),api("/v1/finance/transactions?limit=20")]);
    state.accounts=accounts; state.categories=categories;
    document.querySelector<HTMLDivElement>("#app")!.innerHTML=`<main class="shell"><header><div><span class="eyebrow">FINANCIAL CONTROL</span><h1>Good evening, ${me.display_name}</h1></div><button id="logout" class="secondary">Log out</button></header>
    <section class="grid stats"><div class="card"><span class="muted">Income</span><strong>₸ ${money(summary.income)}</strong></div><div class="card"><span class="muted">Expenses</span><strong>₸ ${money(summary.expenses)}</strong></div><div class="card"><span class="muted">Net</span><strong>₸ ${money(summary.net)}</strong></div><div class="card"><span class="muted">Transactions</span><strong>${summary.transaction_count}</strong></div></section>
    <section class="grid content"><div class="card"><div class="row"><h2>New transaction</h2></div><form id="tx"><label>Type<select name="type"><option value="expense">Expense</option><option value="income">Income</option></select></label><label>Account<select name="account_id">${accounts.map((a:any)=>`<option value="${a.id}">${a.name} · ${a.currency}</option>`).join("")}</select></label><label>Category<select name="category_id"><option value="">None</option>${categories.map((c:any)=>`<option value="${c.id}">${c.name}</option>`).join("")}</select></label><label>Amount<input name="amount" inputmode="decimal" required></label><label>Description<input name="description" maxlength="500"></label><label>Date<input name="transaction_date" type="date" value="${new Date().toISOString().slice(0,10)}" required></label><button>Add transaction</button></form></div>
    <div class="card"><div class="row"><h2>Recent activity</h2><span class="muted">${summary.from_date} → ${summary.to_date}</span></div><div class="table">${txs.map((t:any)=>`<div class="tx"><div><b>${t.description||"Untitled"}</b><small>${t.transaction_date} · ${t.currency}</small></div><strong class="${t.type}">${t.type==="expense"?"−":"+"}${money(t.amount)}</strong></div>`).join("")||`<p class="muted">No transactions yet.</p>`}</div></div></section></main>`;
    document.querySelector("#logout")!.addEventListener("click",()=>{state.token="";localStorage.removeItem(tokenKey);renderLogin();});
    document.querySelector("#tx")!.addEventListener("submit",async(e)=>{e.preventDefault();const f=new FormData(e.currentTarget as HTMLFormElement);try{await api("/v1/finance/transactions",{method:"POST",headers:{"Idempotency-Key":crypto.randomUUID()},body:JSON.stringify({account_id:f.get("account_id"),category_id:f.get("category_id")||null,type:f.get("type"),amount:f.get("amount"),currency:state.accounts.find(a=>a.id===f.get("account_id"))?.currency,description:f.get("description"),transaction_date:f.get("transaction_date")})});renderApp();}catch(err){alert(String(err));}});
  } catch { state.token="";localStorage.removeItem(tokenKey);renderLogin(); }
}

(state.token ? renderApp : renderLogin)();
