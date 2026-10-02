const API = (window as Window & { ENV_API?: string }).ENV_API ?? "http://localhost:8000";
const tokenKey = "expense_tracker_token";
const state = { token: localStorage.getItem(tokenKey) ?? "", accounts: [] as any[], categories: [] as any[] };

const icons = {
  logo:'<svg viewBox="0 0 24 24" fill="none"><rect x="4" y="3" width="16" height="18" rx="4" fill="currentColor" opacity=".18"/><path d="M7.5 16V11M12 16V7M16.5 16v-3" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>',
  mail:'<svg viewBox="0 0 24 24" fill="none"><path d="M4 6.5h16v11H4z" stroke="currentColor" stroke-width="1.8"/><path d="m5 8 7 5 7-5" stroke="currentColor" stroke-width="1.8"/></svg>',
  lock:'<svg viewBox="0 0 24 24" fill="none"><rect x="5" y="10" width="14" height="10" rx="2" stroke="currentColor" stroke-width="1.8"/><path d="M8 10V7a4 4 0 0 1 8 0v3" stroke="currentColor" stroke-width="1.8"/></svg>',
  eye:'<svg viewBox="0 0 24 24" fill="none"><path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="2.5" stroke="currentColor" stroke-width="1.8"/></svg>',
  eyeOff:'<svg viewBox="0 0 24 24" fill="none"><path d="m3 3 18 18M10.6 6.2A9.9 9.9 0 0 1 12 6c6 0 9.5 6 9.5 6a17 17 0 0 1-3.1 3.7M6.1 6.9C3.8 8.6 2.5 12 2.5 12s3.5 6 9.5 6c1.3 0 2.5-.3 3.5-.7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  chart:'<svg viewBox="0 0 24 24" fill="none"><path d="M6 18V11M12 18V6M18 18v-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  pie:'<svg viewBox="0 0 24 24" fill="none"><path d="M12 3v9h9A9 9 0 1 0 12 3Z" stroke="currentColor" stroke-width="1.8"/><path d="M15 3.6A9 9 0 0 1 20.4 9H15V3.6Z" stroke="currentColor" stroke-width="1.8"/></svg>',
  trend:'<svg viewBox="0 0 24 24" fill="none"><path d="m4 16 5-5 4 3 7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M15 7h5v5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  shield:'<svg viewBox="0 0 24 24" fill="none"><path d="M12 3 20 6v5c0 5-3.2 8.5-8 10-4.8-1.5-8-5-8-10V6l8-3Z" stroke="currentColor" stroke-width="1.8"/><path d="m9 12 2 2 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
  arrow:'<svg viewBox="0 0 24 24" fill="none"><path d="M5 12h13M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
};

async function api(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (state.token) headers.set("Authorization", "Bearer " + state.token);
  const res = await fetch(API + path, { ...init, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = body?.detail;
    const message = typeof detail === "string" ? detail : Array.isArray(detail) ? detail.map((x: any) => x?.msg ?? JSON.stringify(x)).join(", ") : detail ? JSON.stringify(detail) : "HTTP " + res.status;
    throw new Error(message);
  }
  return res.status === 204 ? null : res.json();
}

function renderBrandPanel() {
  return '<section class="brand-panel">' +
    '<div class="brand-top"><div class="logo"><span class="logo-mark">' + icons.logo + '</span>Expense Tracker</div><div class="secure-pill"><span class="secure-dot"></span>Secure &amp; Private</div></div>' +
    '<div class="brand-copy"><h1>Take control of<br>your <span>finances</span></h1><p>Track expenses, manage budgets, and build better financial habits with a simple and powerful tool.</p>' +
    '<div class="feature-list">' +
    '<div class="feature"><span class="feature-icon">' + icons.chart + '</span><div><strong>Track Expenses</strong><span>See where your money goes</span></div></div>' +
    '<div class="feature"><span class="feature-icon">' + icons.pie + '</span><div><strong>Set Budgets</strong><span>Stay on top of your goals</span></div></div>' +
    '<div class="feature"><span class="feature-icon">' + icons.trend + '</span><div><strong>Visual Insights</strong><span>Understand your spending</span></div></div>' +
    '<div class="feature"><span class="feature-icon">' + icons.shield + '</span><div><strong>Your Data, Your Control</strong><span>Private, secure, and auditable</span></div></div></div></div>' +
    '<div class="dashboard-preview" aria-hidden="true"><div class="dash-window"><div class="dash-nav"><b>▣ Expense Tracker</b><span style="margin-left:auto;color:#8793a7">Dashboard</span></div><div class="dash-body"><aside class="dash-side"><div class="active">⌂ Dashboard</div><div>☷ Transactions</div><div>◉ Categories</div><div>▣ Budgets</div><div>⌁ Reports</div><div>⚙ Settings</div></aside><div class="dash-main"><div class="dash-title">Dashboard</div><div class="dash-stat"><small>Total Expenses</small><strong>$1,250.00</strong><small>↓ 12% from last month</small></div><div class="dash-chart"><small>Expenses Overview</small><div class="bars"><i></i><i></i><i></i><i></i><i></i></div></div></div></div></div></div>' +
    '<div class="quote"><div class="quote-mark">“</div><p>A simple and beautiful way to manage personal finances.</p><div class="stars">★★★★★</div></div></section>';
}

function inputField(name: string, label: string, type: string, placeholder: string, icon: string, password = false) {
  return '<div class="field"><label for="' + name + '">' + label + '</label><div class="input-wrap"><span class="input-icon">' + icon + '</span><input id="' + name + '" name="' + name + '" type="' + type + '" placeholder="' + placeholder + '" autocomplete="' + (password ? "current-password" : "email") + '" required>' +
    (password ? '<button type="button" class="toggle-password" data-target="' + name + '" aria-label="Show password">' + icons.eye + '</button>' : '') +
    '</div></div>';
}

function renderAuth(mode: "login" | "register" = "login") {
  const isLogin = mode === "login";
  document.querySelector<HTMLDivElement>("#app")!.innerHTML =
    '<main class="auth-page"><div class="auth-shell">' + renderBrandPanel() +
    '<section class="form-panel"><div class="auth-card"><div class="auth-logo"><span class="logo-mark">' + icons.logo + '</span>Expense Tracker</div>' +
    '<div class="auth-heading"><h2>' + (isLogin ? "Welcome back" : "Create your account") + '</h2><p>' + (isLogin ? "Sign in to your account to continue" : "Start taking control of your finances today") + '</p></div>' +
    '<div class="auth-tabs"><button class="auth-tab ' + (isLogin ? "active" : "") + '" data-mode="login">Sign in</button><button class="auth-tab ' + (!isLogin ? "active" : "") + '" data-mode="register">Create account</button></div>' +
    '<form id="auth-form" class="form">' +
    (isLogin ? "" : inputField("display_name","Full name","text","Your name",icons.chart)) +
    inputField("email","Email address","email","you@example.com",icons.mail) +
    inputField("password","Password","password",isLogin ? "Enter your password" : "At least 10 characters",icons.lock,true) +
    (isLogin ? "" : inputField("confirm_password","Confirm password","password","Repeat your password",icons.lock,true)) +
    (isLogin ? '<div class="form-meta"><label class="remember"><input type="checkbox" name="remember" checked> Remember me</label><button type="button" class="link" id="forgot">Forgot password?</button></div>' : '<div class="form-meta"><span class="muted">Use at least 10 characters.</span></div>') +
    '<button class="primary-btn" id="submit-auth" type="submit">' + (isLogin ? "Sign in" : "Create account") + ' <span style="display:inline-block;margin-left:8px;vertical-align:-5px">' + icons.arrow + '</span></button><p id="error" class="form-error"></p></form>' +
    '<div class="divider"><span>Or continue with</span></div><div class="social-grid"><button class="social-btn" type="button" disabled>Google</button><button class="social-btn" type="button" disabled>GitHub</button></div>' +
    '<p class="social-note">Social sign-in will be available after OAuth is configured.</p><p class="terms">By continuing, you agree to our <a href="#" onclick="return false">Terms of Service</a> and <a href="#" onclick="return false">Privacy Policy</a>.</p>' +
    '</div></section></div></main>';

  document.querySelectorAll<HTMLButtonElement>(".auth-tab").forEach(btn => btn.addEventListener("click", () => renderAuth(btn.dataset.mode as "login" | "register")));
  document.querySelectorAll<HTMLButtonElement>(".toggle-password").forEach(btn => btn.addEventListener("click", () => {
    const input = document.getElementById(btn.dataset.target!) as HTMLInputElement;
    input.type = input.type === "password" ? "text" : "password";
    btn.innerHTML = input.type === "password" ? icons.eye : icons.eyeOff;
  }));
  document.querySelector("#forgot")?.addEventListener("click", () => {
    (document.querySelector("#error") as HTMLElement).textContent = "Password recovery is not configured yet.";
  });
  document.querySelector("#auth-form")!.addEventListener("submit", async (e) => {
    e.preventDefault();
    const f = new FormData(e.currentTarget as HTMLFormElement);
    const error = document.querySelector("#error") as HTMLElement;
    const submit = document.querySelector("#submit-auth") as HTMLButtonElement;
    error.textContent = "";
    if (!isLogin && f.get("password") !== f.get("confirm_password")) { error.textContent = "Passwords do not match."; return; }
    submit.disabled = true;
    try {
      const endpoint = isLogin ? "/v1/auth/login" : "/v1/auth/register";
      const body = isLogin
        ? { email: f.get("email"), password: f.get("password") }
        : { email: f.get("email"), password: f.get("password"), display_name: f.get("display_name"), base_currency: "UZS" };
      const result = await api(endpoint, { method:"POST", body:JSON.stringify(body) });
      state.token = result.access_token;
      localStorage.setItem(tokenKey, state.token);
      await renderApp();
    } catch (err) {
      error.textContent = err instanceof Error ? err.message : String(err);
      submit.disabled = false;
    }
  });
}

function money(v: unknown) { return new Intl.NumberFormat("uz-UZ", { maximumFractionDigits: 0 }).format(Number(v)); }

async function renderApp() {
  try {
    const [me, accounts, categories, summary, txs] = await Promise.all([api("/v1/auth/me"),api("/v1/finance/accounts"),api("/v1/finance/categories"),api("/v1/finance/summary"),api("/v1/finance/transactions?limit=20")]);
    state.accounts=accounts; state.categories=categories;
    document.querySelector<HTMLDivElement>("#app")!.innerHTML='<main class="shell"><header><div><span class="eyebrow">FINANCIAL CONTROL · '+String(me.role).toUpperCase()+'</span><h1>Good evening, '+me.display_name+'</h1></div><button id="logout" class="secondary">Log out</button></header>' +
      '<section class="grid stats"><div class="card"><span class="muted">Income</span><strong>₸ '+money(summary.income)+'</strong></div><div class="card"><span class="muted">Expenses</span><strong>₸ '+money(summary.expenses)+'</strong></div><div class="card"><span class="muted">Net</span><strong>₸ '+money(summary.net)+'</strong></div><div class="card"><span class="muted">Transactions</span><strong>'+summary.transaction_count+'</strong></div></section>' +
      '<section class="grid content"><div class="card"><div class="row"><h2>New transaction</h2></div><form id="tx"><label>Type<select name="type"><option value="expense">Expense</option><option value="income">Income</option></select></label><label>Account<select name="account_id">'+accounts.map((a:any)=>'<option value="'+a.id+'">'+a.name+' · '+a.currency+'</option>').join("")+'</select></label><label>Category<select name="category_id"><option value="">None</option>'+categories.map((c:any)=>'<option value="'+c.id+'">'+c.name+'</option>').join("")+'</select></label><label>Amount<input name="amount" inputmode="decimal" required></label><label>Description<input name="description" maxlength="500"></label><label>Date<input name="transaction_date" type="date" value="'+new Date().toISOString().slice(0,10)+'" required></label><button>Add transaction</button></form></div>' +
      '<div class="card"><div class="row"><h2>Recent activity</h2><span class="muted">'+summary.from_date+' → '+summary.to_date+'</span></div><div class="table">'+txs.map((t:any)=>'<div class="tx"><div><b>'+String(t.description||"Untitled")+'</b><small>'+t.transaction_date+' · '+t.currency+'</small></div><strong class="'+t.type+'">'+(t.type==="expense"?"−":"+")+money(t.amount)+'</strong></div>').join("")+'</div></div></section></main>';
    document.querySelector("#logout")!.addEventListener("click",()=>{state.token="";localStorage.removeItem(tokenKey);renderAuth("login");});
    document.querySelector("#tx")!.addEventListener("submit",async(e)=>{e.preventDefault();const f=new FormData(e.currentTarget as HTMLFormElement);try{await api("/v1/finance/transactions",{method:"POST",headers:{"Idempotency-Key":crypto.randomUUID()},body:JSON.stringify({account_id:f.get("account_id"),category_id:f.get("category_id")||null,type:f.get("type"),amount:f.get("amount"),currency:state.accounts.find(a=>a.id===f.get("account_id"))?.currency,description:f.get("description"),transaction_date:f.get("transaction_date")})});renderApp();}catch(err){alert(err instanceof Error?err.message:String(err));}});
  } catch { state.token="";localStorage.removeItem(tokenKey);renderAuth("login"); }
}

(state.token ? renderApp() : renderAuth("login"));
