import { chromium } from "playwright";
import fs from "node:fs/promises";
import path from "node:path";

const output = path.join(process.cwd(), "artifacts", "visual-qa");
await fs.mkdir(output, { recursive: true });
const browser = await chromium.launch({
  headless: true,
});
const consoleErrors = [];
const frameworkBootstrapProbes = [];
const baseUrl = "http://127.0.0.1:8501/app";
const monitoredPages = new WeakSet();

function monitorPage(page) {
  if (monitoredPages.has(page)) return;
  monitoredPages.add(page);
  page.on("response", (response) => {
    if (response.status() < 400) return;
    const url = response.url();
    if (
      response.status() === 404 &&
      /\/(customers|predict|customer-detail|batch|analytics|model|model-explanations)\/_stcore\/(health|host-config)$/.test(
        url,
      )
    ) {
      frameworkBootstrapProbes.push(url);
      return;
    }
    consoleErrors.push(`HTTP ${response.status()}: ${url}`);
  });
  page.on("console", (message) => {
    if (
      message.type() === "error" &&
      !message.text().startsWith("Failed to load resource:")
    ) {
      consoleErrors.push(`${page.url()}: ${message.text()}`);
    }
  });
  page.on("pageerror", (error) => consoleErrors.push(error.message));
}

async function createPage(url, width, height = 1000) {
  const page = await browser.newPage({ viewport: { width, height } });
  page.context().on("page", monitorPage);
  monitorPage(page);
  await page.goto(url, { waitUntil: "networkidle" });
  return page;
}

async function capture(page, filename, fullPage = false) {
  await page.screenshot({ path: path.join(output, filename), fullPage });
}

async function choose(page, label, option) {
  await page
    .getByRole("combobox", { name: new RegExp(`${label}$`) })
    .click();

  // Tenure labels can contain different dash characters after copy/paste.
  const optionLocator =
    label === "Tenure"
      ? page.getByRole("option", { name: /0.*12 months/ })
      : page.getByRole("option", { name: option, exact: true });

  await optionLocator.click();
}

async function assertNoOverflow(page, context) {
  const layout = await page.evaluate(() => {
    const main = document.querySelector('[data-testid="stMain"]');
    return {
      bodyOverflow: document.body.scrollWidth > window.innerWidth,
      mainOverflow: main ? main.scrollWidth > main.clientWidth : false,
    };
  });
  if (layout.bodyOverflow || layout.mainOverflow) {
    throw new Error(`Horizontal overflow in ${context}: ${JSON.stringify(layout)}`);
  }
}

async function loadDemoBatch(page, expected = "Dataset ready") {
  await choose(page, "Dataset source", "Approved demo batch");
  await page
    .getByRole("button", { name: "Load and validate demo batch" })
    .click();
  await page.getByText(expected).waitFor();
}

async function runDemoBatch(page) {
  await page
    .getByRole("button", { name: "Run deterministic batch analysis" })
    .click();
  await page.getByRole("heading", { name: "Batch results" }).waitFor();
}

async function loadLocalExplanation(page, customerId) {
  await choose(page, "Approved explanation customer", customerId);
  await page.getByRole("button", { name: "Load demo explanation" }).click();
  await page
    .locator(".ex-local-head")
    .getByText(customerId, { exact: true })
    .waitFor();
}

const viewports = [375, 768, 1024, 1440];

console.log("runtime:warm-router");
const routerWarmup = await createPage(`${baseUrl}/`, 1440);
await routerWarmup.getByRole("heading", { name: "Command Center" }).waitFor();
await routerWarmup.close();

for (const width of viewports) {
  console.log(`model-explanations:${width}`);
  const page = await createPage(
    `${baseUrl}/model-explanations?fixture=CUST-HARD-001`,
    width,
    width === 375 ? 900 : 1000,
  );
  await page
    .getByRole("heading", { name: "Model Explanations", exact: true })
    .waitFor();
  await page.getByText("Demo explanation view", { exact: true }).waitFor();
  await page
    .locator(".ex-local-head")
    .getByText("CUST-HARD-001", { exact: true })
    .waitFor();
  await page.waitForTimeout(400);
  await assertNoOverflow(page, `model-explanations-${width}`);
  const presentation = await page.evaluate(() => ({
    tableVisible:
      getComputedStyle(document.querySelector(".ex-global-table")).display !==
      "none",
    globalListVisible:
      getComputedStyle(document.querySelector(".ex-global-list")).display !==
      "none",
  }));
  if (!presentation.globalListVisible) {
    throw new Error(`Global explanation list missing at ${width}px`);
  }
  if (width <= 1024 && presentation.tableVisible) {
    throw new Error(`Dense explanation table remained visible at ${width}px`);
  }
  if (width === 1440 && !presentation.tableVisible) {
    throw new Error("Desktop explanation table missing at 1440px");
  }
  await capture(page, `model-explanations-${width}.png`);
  if (width === 375 || width === 1440) {
    await page.locator(".ex-local-head").scrollIntoViewIfNeeded();
    await capture(page, `model-explanations-local-${width}.png`);
  }
  await page.close();
}

console.log("model-explanations:idle");
const explanationIdle = await createPage(`${baseUrl}/model-explanations`, 1440);
await explanationIdle
  .getByRole("heading", { name: "Model Explanations", exact: true })
  .waitFor();
await explanationIdle.getByText("No customer explanation selected").waitFor();
await capture(explanationIdle, "model-explanations-idle-1440.png");
await explanationIdle.close();

for (const [state, expected, filename] of [
  [
    "Empty demo view",
    "No global explanation rows",
    "model-explanations-global-empty-1440.png",
  ],
  [
    "Explanation unavailable",
    "Global explanation unavailable",
    "model-explanations-global-unavailable-1440.png",
  ],
]) {
  console.log(`model-explanations:global:${state}`);
  const page = await createPage(`${baseUrl}/model-explanations`, 1440);
  await page.getByText("Demo state controls", { exact: true }).click({ force: true });
  await choose(page, "Global explanation state", state);
  await page.getByText(expected).waitFor();
  await assertNoOverflow(page, `model-explanations-${state}`);
  await capture(page, filename);
  await page.close();
}

for (const [state, expected, filename] of [
  [
    "Malformed global data",
    "The demo global explanation data could not be interpreted.",
    "model-explanations-global-malformed-1440.png",
  ],
  [
    "Global service error",
    "Global explanation data could not be loaded.",
    "model-explanations-global-error-1440.png",
  ],
]) {
  console.log(`model-explanations:global:${state}`);
  const page = await createPage(`${baseUrl}/model-explanations`, 1440);
  await page.getByText("Demo state controls", { exact: true }).click({ force: true });
  await choose(page, "Global explanation state", state);
  await page.getByText(expected).waitFor();
  await capture(page, filename);
  await page.getByRole("button", { name: "Retry global explanation" }).click();
  await page.getByText("Demo explanation view", { exact: true }).waitFor();
  await page.close();
}

for (const [fixture, probability, filename] of [
  ["CUST-LOW-001", "11%", "model-explanations-local-low-1440.png"],
  ["CUST-HIGH-001", "87%", "model-explanations-local-high-1440.png"],
  [
    "CUST-BORDERLINE-001",
    "52%",
    "model-explanations-local-borderline-1440.png",
  ],
  ["CUST-HARD-001", "61%", "model-explanations-local-hard-1440.png"],
]) {
  console.log(`model-explanations:local:${fixture}`);
  const page = await createPage(
    `${baseUrl}/model-explanations?fixture=${fixture}`,
    1440,
  );
  await page.locator(".ex-local-head").getByText(fixture, { exact: true }).waitFor();
  await page.locator(".ex-risk").getByText(probability, { exact: true }).waitFor();
  await page.locator(".ex-local-head").scrollIntoViewIfNeeded();
  await capture(page, filename);
  await page.close();
}

console.log("model-explanations:unknown");
const explanationUnknown = await createPage(
  `${baseUrl}/model-explanations?fixture=UNKNOWN`,
  1440,
);
await explanationUnknown.getByText("Customer explanation not found").waitFor();
await capture(explanationUnknown, "model-explanations-unknown-1440.png");
await explanationUnknown.close();

for (const [state, expected, filename] of [
  [
    "Explanation unavailable",
    "No explanation available for CUST-HIGH-001",
    "model-explanations-local-unavailable-1440.png",
  ],
  [
    "Malformed explanation",
    "Explanation data cannot be interpreted",
    "model-explanations-local-malformed-1440.png",
  ],
  [
    "Local service error",
    "Explanation service unavailable",
    "model-explanations-local-error-1440.png",
  ],
]) {
  console.log(`model-explanations:local:${state}`);
  const page = await createPage(`${baseUrl}/model-explanations`, 1440);
  await page.getByText("Demo state controls", { exact: true }).click({ force: true });
  await choose(page, "Local explanation state", state);
  await loadLocalExplanation(page, "CUST-HIGH-001").catch(async () => {
    await page.getByText(expected).waitFor();
  });
  await page.getByText(expected).waitFor();
  await capture(page, filename);
  if (state !== "Explanation unavailable") {
    await page
      .getByRole("button", { name: "Retry customer explanation" })
      .click();
    await page.locator(".ex-local-head").getByText("CUST-HIGH-001").waitFor();
  }
  await page.close();
}

console.log("model-explanations:navigation");
const explanationNavigation = await createPage(
  `${baseUrl}/customer-detail?fixture=CUST-HIGH-001`,
  1440,
);
const explanationPromise = explanationNavigation.context().waitForEvent("page");
await explanationNavigation
  .getByRole("link", { name: "Open demo explanation for CUST-HIGH-001" })
  .click();
const explanationPage = await explanationPromise;
await explanationPage.waitForURL(
  "**/app/model-explanations?fixture=CUST-HIGH-001",
);
await explanationPage
  .locator(".ex-local-head")
  .getByText("CUST-HIGH-001", { exact: true })
  .waitFor();
await capture(
  explanationPage,
  "model-explanations-customer-detail-navigation-1440.png",
);
await explanationPage.close();
await explanationNavigation.close();

for (const width of viewports) {
  console.log(`model:${width}`);
  const page = await createPage(
    `${baseUrl}/model`,
    width,
    width === 375 ? 900 : 1000,
  );
  await page.getByRole("heading", { name: "Model", exact: true }).waitFor();
  await page
    .getByText("Deterministic fixture contract available", { exact: true })
    .first()
    .waitFor();
  await page.getByText("demo-fixture-v1.0.0", { exact: true }).waitFor();
  await page.waitForTimeout(400);
  await assertNoOverflow(page, `model-${width}`);
  const presentation = await page.evaluate(() => ({
    tableVisible:
      getComputedStyle(document.querySelector(".mo-candidate-table")).display !==
      "none",
    mobileVisible:
      getComputedStyle(document.querySelector(".mo-mobile-candidates")).display !==
      "none",
  }));
  if (width <= 1024 && (!presentation.mobileVisible || presentation.tableVisible)) {
    throw new Error(`Mobile Model candidate presentation missing at ${width}px`);
  }
  if (width === 1440 && (!presentation.tableVisible || presentation.mobileVisible)) {
    throw new Error("Desktop Model candidate table missing at 1440px");
  }
  await capture(page, `model-${width}.png`);
  if (width === 375 || width === 1440) {
    await page
      .getByRole("heading", { name: "Candidate comparison", exact: true })
      .scrollIntoViewIfNeeded();
    await capture(page, `model-candidates-${width}.png`);
  }
  await page.close();
}

console.log("model:unavailable");
const modelUnavailable = await createPage(`${baseUrl}/model`, 1440);
await modelUnavailable
  .getByText("Demo state controls", { exact: true })
  .click({ force: true });
await choose(modelUnavailable, "Model data state", "Model unavailable");
await modelUnavailable
  .getByText("No model information is currently available")
  .waitFor();
await modelUnavailable
  .getByText("No current model value", { exact: true })
  .waitFor();
await assertNoOverflow(modelUnavailable, "model-unavailable");
await capture(modelUnavailable, "model-unavailable-1440.png");
await modelUnavailable.close();

console.log("model:error-recovery");
const modelError = await createPage(`${baseUrl}/model`, 1440);
await modelError
  .getByText("Demo state controls", { exact: true })
  .click({ force: true });
await choose(modelError, "Model data state", "Malformed model metadata");
await modelError
  .getByText(
    "The demo model metadata could not be loaded. No model or customer data was changed.",
  )
  .waitFor();
await capture(modelError, "model-error-1440.png");
await modelError
  .getByRole("button", { name: "Retry demo model context" })
  .click();
await modelError
  .getByText("Deterministic fixture contract available", { exact: true })
  .first()
  .waitFor();
await modelError.close();

for (const width of viewports) {
  console.log(`analytics:${width}`);
  const page = await createPage(
    `${baseUrl}/analytics`,
    width,
    width === 375 ? 900 : 1000,
  );
  await page.getByRole("heading", { name: "Analytics", exact: true }).waitFor();
  await page.getByText("52.8%", { exact: true }).waitFor();
  await page.getByText("Rate not available").waitFor();
  await page
    .locator(width <= 1024 ? ".an-mobile-segments" : ".an-segment-table")
    .getByText("Month-to-month", { exact: true })
    .waitFor();
  await page.waitForTimeout(400);
  await assertNoOverflow(page, `analytics-${width}`);
  const presentation = await page.evaluate(() => ({
    tableVisible:
      getComputedStyle(document.querySelector(".an-segment-table")).display !==
      "none",
    mobileVisible:
      getComputedStyle(document.querySelector(".an-mobile-segments")).display !==
      "none",
  }));
  if (width <= 1024 && (!presentation.mobileVisible || presentation.tableVisible)) {
    throw new Error(`Mobile analytics presentation missing at ${width}px`);
  }
  if (width === 1440 && (!presentation.tableVisible || presentation.mobileVisible)) {
    throw new Error("Desktop analytics table presentation missing at 1440px");
  }
  await capture(page, `analytics-${width}.png`, width === 375);
  if (width === 375 || width === 1440) {
    await page
      .getByRole("heading", { name: "Segment breakdown", exact: true })
      .scrollIntoViewIfNeeded();
    await capture(page, `analytics-segments-${width}.png`);
  }
  await page.close();
}

console.log("analytics:filter");
const analyticsFilter = await createPage(`${baseUrl}/analytics`, 1440);
await choose(analyticsFilter, "Segment breakdown", "Payment method");
await analyticsFilter
  .getByText("Electronic check", { exact: true })
  .first()
  .waitFor();
await analyticsFilter.getByText("74.0%", { exact: true }).first().waitFor();
await capture(analyticsFilter, "analytics-payment-filter-1440.png");
await analyticsFilter.close();

console.log("analytics:empty");
const analyticsEmpty = await createPage(`${baseUrl}/analytics`, 1440);
await analyticsEmpty
  .getByText("Demo state controls", { exact: true })
  .click({ force: true });
await choose(analyticsEmpty, "Analytics data state", "Empty analytics");
await analyticsEmpty.getByText("No analytics data available").waitFor();
await assertNoOverflow(analyticsEmpty, "analytics-empty");
await capture(analyticsEmpty, "analytics-empty-1440.png");
await analyticsEmpty.close();

console.log("analytics:error-recovery");
const analyticsError = await createPage(`${baseUrl}/analytics`, 1440);
await analyticsError
  .getByText("Demo state controls", { exact: true })
  .click({ force: true });
await choose(analyticsError, "Analytics data state", "Malformed analytics");
await analyticsError
  .getByText(
    "The demo analytics snapshot could not be loaded. No customer data was changed.",
  )
  .waitFor();
await capture(analyticsError, "analytics-error-1440.png");
await analyticsError
  .getByRole("button", { name: "Retry sample analytics" })
  .click();
await analyticsError.getByText("52.8%", { exact: true }).waitFor();
await analyticsError.close();

for (const width of viewports) {
  console.log(`batch:${width}`);
  const page = await createPage(
    `${baseUrl}/batch`,
    width,
    width === 375 ? 900 : 1000,
  );
  await page.getByRole("heading", { name: "Batch Prediction" }).waitFor();
  await loadDemoBatch(page);
  await runDemoBatch(page);
  await page
    .locator(width <= 1024 ? ".bp-mobile-results" : ".bp-results-table")
    .getByText("CUST-HIGH-001", { exact: true })
    .waitFor();
  await page.waitForTimeout(400);
  await assertNoOverflow(page, `batch-${width}`);
  await page.evaluate(() =>
    document.querySelector('[data-testid="stMain"]')?.scrollTo(0, 0),
  );
  await capture(page, `batch-${width}.png`);
  if (width === 375) {
    await page
      .getByRole("button", { name: "Inspect CUST-HIGH-001" })
      .scrollIntoViewIfNeeded();
    await capture(page, "batch-375-priority.png");
  }
  await page.close();
}

console.log("batch:initial");
const batchInitial = await createPage(`${baseUrl}/batch`, 1440);
await batchInitial.getByRole("heading", { name: "Batch Prediction" }).waitFor();
await batchInitial.getByText("No dataset selected").waitFor();
await capture(batchInitial, "batch-initial-1440.png");
await batchInitial.close();

console.log("batch:valid-validation");
const batchValid = await createPage(`${baseUrl}/batch`, 1440);
await loadDemoBatch(batchValid);
await batchValid.getByText("4", { exact: true }).first().waitFor();
await capture(batchValid, "batch-valid-validation-1440.png");
await batchValid.close();

for (const [mode, expected, filename] of [
  ["Invalid approved batch", "Dataset blocked", "batch-invalid-1440.png"],
  ["Empty approved batch", "Dataset is empty", "batch-empty-1440.png"],
  [
    "Malformed approved batch",
    "Dataset cannot be read",
    "batch-malformed-1440.png",
  ],
]) {
  console.log(`batch:${mode}`);
  const page = await createPage(`${baseUrl}/batch`, 1440);
  await page.getByText("Demo state controls", { exact: true }).click({ force: true });
  await choose(page, "Approved batch state", mode);
  await loadDemoBatch(page, expected);
  const runButton = page.getByRole("button", {
    name: "Run deterministic batch analysis",
  });
  if (!(await runButton.isDisabled())) {
    throw new Error(`${mode} did not disable batch analysis`);
  }
  await capture(page, filename);
  await page.close();
}

console.log("batch:upload");
const batchUpload = await createPage(`${baseUrl}/batch`, 1440);
await choose(batchUpload, "Dataset source", "Upload CSV");
const uploadCsv = [
  "customerID,gender,SeniorCitizen,Partner,Dependents,tenure,PhoneService,MultipleLines,InternetService,OnlineSecurity,OnlineBackup,DeviceProtection,TechSupport,StreamingTV,StreamingMovies,Contract,PaperlessBilling,PaymentMethod,MonthlyCharges,TotalCharges",
  'CUST-LOW-001,Male,0,Yes,Yes,48,Yes,Yes,DSL,Yes,Yes,Yes,Yes,No,No,Two year,No,Bank transfer (automatic),68.75,3300.0',
].join("\n");
await batchUpload.locator('input[type="file"]').setInputFiles({
  name: "approved-upload.csv",
  mimeType: "text/csv",
  buffer: Buffer.from(uploadCsv),
});
await batchUpload.getByRole("button", { name: "Validate uploaded CSV" }).click();
await batchUpload.getByText("Dataset ready").waitFor();
await capture(batchUpload, "batch-upload-valid-1440.png");
await batchUpload.close();

console.log("batch:error-recovery");
const batchError = await createPage(`${baseUrl}/batch`, 1440);
await batchError.getByText("Demo state controls", { exact: true }).click({ force: true });
await batchError
  .getByText("Force one batch service error", { exact: true })
  .click();
await loadDemoBatch(batchError);
await batchError
  .getByRole("button", { name: "Run deterministic batch analysis" })
  .click();
await batchError
  .getByText("The demo batch service did not complete the analysis.")
  .waitFor();
await capture(batchError, "batch-error-1440.png");
await batchError.getByRole("button", { name: "Retry batch analysis" }).click();
await batchError.getByRole("heading", { name: "Batch results" }).waitFor();
await batchError.close();

console.log("batch:inspection");
const batchNavigation = await createPage(`${baseUrl}/batch`, 1440);
await loadDemoBatch(batchNavigation);
await runDemoBatch(batchNavigation);
await batchNavigation
  .getByRole("button", { name: "Inspect CUST-HIGH-001" })
  .click();
await batchNavigation.waitForURL("**/app/customer-detail?fixture=CUST-HIGH-001");
await batchNavigation
  .getByRole("heading", { name: "CUST-HIGH-001" })
  .waitFor();
await batchNavigation.waitForTimeout(500);
if (await batchNavigation.getByText("Page not found", { exact: true }).isVisible().catch(() => false)) {
  throw new Error("Batch inspection opened with a visible route-fallback error");
}
await capture(batchNavigation, "batch-inspection-1440.png");
await batchNavigation.close();

for (const width of viewports) {
  console.log(`customer-detail:${width}`);
  const page = await createPage(
    `${baseUrl}/customer-detail?fixture=CUST-HIGH-001`,
    width,
    width === 375 ? 900 : 1000,
  );
  await page.getByRole("heading", { name: "CUST-HIGH-001" }).waitFor();
  await page.getByText("87%", { exact: true }).first().waitFor();
  await page.waitForTimeout(400);
  await assertNoOverflow(page, `customer-detail-${width}`);
  await capture(page, `customer-detail-${width}.png`);
  if (width === 375) {
    await page.getByRole("heading", { name: "Top drivers" }).scrollIntoViewIfNeeded();
    await capture(page, "customer-detail-375-drivers.png");
  }
  if (width === 1440) {
    await page
      .getByRole("heading", { name: "Customer and account context" })
      .scrollIntoViewIfNeeded();
    await capture(page, "customer-detail-context-1440.png");
  }
  await page.close();
}

for (const [fixture, expected, filename] of [
  ["CUST-LOW-001", "11%", "customer-detail-low-1440.png"],
  ["CUST-BORDERLINE-001", "52%", "customer-detail-borderline-1440.png"],
  ["CUST-HARD-001", "61%", "customer-detail-hard-1440.png"],
]) {
  console.log(`customer-detail:${fixture}`);
  const page = await createPage(
    `${baseUrl}/customer-detail?fixture=${fixture}`,
    1440,
  );
  await page.getByRole("heading", { name: fixture }).waitFor();
  await page.getByText(expected, { exact: true }).first().waitFor();
  await assertNoOverflow(page, `customer-detail-${fixture}`);
  await capture(page, filename);
  await page.close();
}

console.log("customer-detail:missing");
const missingDetail = await createPage(`${baseUrl}/customer-detail`, 1440);
await missingDetail.getByRole("heading", { name: "Select a customer" }).waitFor();
await missingDetail.getByText("No customer selected").waitFor();
await capture(missingDetail, "customer-detail-missing-1440.png");
await missingDetail.close();

console.log("customer-detail:unknown");
const unknownDetail = await createPage(
  `${baseUrl}/customer-detail?fixture=UNKNOWN`,
  1440,
);
await unknownDetail.getByRole("heading", { name: "Customer not found" }).waitFor();
await unknownDetail.getByText("UNKNOWN is not available").waitFor();
await capture(unknownDetail, "customer-detail-unknown-1440.png");
await unknownDetail.close();

console.log("customer-detail:error");
const errorDetail = await createPage(
  `${baseUrl}/customer-detail?fixture=CUST-HIGH-001`,
  1440,
);
await errorDetail.getByText("Demo state controls", { exact: true }).click({ force: true });
await choose(errorDetail, "Customer Detail data state", "Malformed demo record");
await errorDetail
  .getByText(
    "The demo customer record could not be loaded. No customer data was changed.",
  )
  .waitFor();
await capture(errorDetail, "customer-detail-error-1440.png");
await errorDetail.close();

for (const width of viewports) {
  console.log(`customer-history:${width}`);
  const page = await createPage(
    `${baseUrl}/customers`,
    width,
    width === 375 ? 900 : 1000,
  );
  await page.getByRole("heading", { name: "Customer History" }).waitFor();
  await page
    .getByText("CUST-HIGH-001", { exact: true })
    .nth(width <= 1024 ? 1 : 0)
    .waitFor();
  await page.waitForTimeout(500);
  await assertNoOverflow(page, `customer-history-${width}`);
  const presentation = await page.evaluate(() => ({
    tableVisible:
      getComputedStyle(document.querySelector(".ch-table-wrap")).display !== "none",
    mobileVisible:
      getComputedStyle(document.querySelector(".ch-mobile-list")).display !== "none",
  }));
  if (width <= 1024 && (!presentation.mobileVisible || presentation.tableVisible)) {
    throw new Error(`Mobile history presentation missing at ${width}px`);
  }
  if (width === 1440 && (!presentation.tableVisible || presentation.mobileVisible)) {
    throw new Error("Desktop semantic table presentation missing at 1440px");
  }
  await capture(page, `customer-history-${width}.png`, width === 375);
  if (width === 375) {
    await page
      .getByRole("link", { name: "Inspect CUST-HIGH-001" })
      .scrollIntoViewIfNeeded();
    await capture(page, "customer-history-375-record.png");
  }
  await page.close();
}

console.log("customer-history:search-clear");
const search = await createPage(`${baseUrl}/customers`, 1440);
const searchInput = search.getByRole("textbox", { name: "Search customer history" });
await searchInput.fill("CUST-LOW-001");
await searchInput.press("Enter");
await search.getByText("1 of 4 approved sample customers shown").waitFor();
await capture(search, "customer-history-search-1440.png");
await search.getByRole("button", { name: "Clear", exact: true }).click();
await search.getByText("4 of 4 approved sample customers shown").waitFor();
await search.close();

console.log("customer-history:filters-date-sort");
const filters = await createPage(`${baseUrl}/customers`, 1440);

await choose(filters, "Risk", "High");
await filters.getByText("2 of 4 approved sample customers shown").waitFor();

await choose(filters, "Contract", "Month-to-month");
await filters.getByText("1 of 4 approved sample customers shown").waitFor();

await choose(filters, "Tenure", "0???12 months");
await choose(filters, "Prediction date", "04 Oct 2026");

await filters.getByText("CUST-HIGH-001", { exact: true }).first().waitFor();
await capture(filters, "customer-history-combined-filters-1440.png");

await filters.getByRole("button", { name: "Reset all" }).click();
await filters.getByText("4 of 4 approved sample customers shown").waitFor();

await choose(filters, "Sort", "Lowest risk first");

try {
  await filters.waitForFunction(() => {
    const rows = [...document.querySelectorAll(".ch-table tbody tr")];
    const firstCustomer = rows[0]?.querySelector("th")?.textContent?.trim();

    return rows.length === 4 && firstCustomer === "CUST-LOW-001";
  }, { timeout: 15000 });
} catch {
  const diagnostic = await filters.evaluate(() => ({
    rows: [...document.querySelectorAll(".ch-table tbody tr")].map((row) => ({
      customer: row.querySelector("th")?.textContent?.trim(),
      probability: row.querySelector(".ch-probability")?.textContent?.trim(),
    })),
    comboboxes: [...document.querySelectorAll('[role="combobox"]')].map(
      (element) => element.innerText,
    ),
  }));

  throw new Error(
    `Customer history sort failed: ${JSON.stringify(diagnostic)}`,
  );
}

await capture(filters, "customer-history-sort-1440.png");
await filters.close();

console.log("customer-history:no-search-results");
const noSearch = await createPage(`${baseUrl}/customers`, 1440);
const noSearchInput = noSearch.getByRole("textbox", {
  name: "Search customer history",
});
await noSearchInput.fill("NO-SUCH-CUSTOMER");
await noSearchInput.press("Enter");
await noSearch.getByText("No customers match this search").waitFor();
await capture(noSearch, "customer-history-no-search-results-1440.png");
await noSearch.close();

console.log("customer-history:no-filter-results");
const noFilter = await createPage(`${baseUrl}/customers`, 1440);
await choose(noFilter, "Risk", "Low");
await choose(noFilter, "Contract", "Month-to-month");
await noFilter.getByText("No customers match these filters").waitFor();
await capture(noFilter, "customer-history-no-filter-results-1440.png");
await noFilter.close();

console.log("customer-history:empty");
const empty = await createPage(`${baseUrl}/customers`, 1440);
await empty.getByText("Demo state controls", { exact: true }).click({ force: true });
await choose(empty, "Customer History data state", "Empty demo history");
await empty.getByText("No customer history exists").waitFor();
await capture(empty, "customer-history-empty-1440.png");
await empty.close();

console.log("customer-history:error");
const malformed = await createPage(`${baseUrl}/customers`, 1440);
await malformed.getByText("Demo state controls", { exact: true }).click({ force: true });
await choose(malformed, "Customer History data state", "Malformed demo history");
await malformed
  .getByText(
    "The demo customer history could not be loaded. No customer data was changed.",
  )
  .waitFor();
await capture(malformed, "customer-history-error-1440.png");
await malformed.close();

console.log("customer-history:inspection");
const navigation = await createPage(`${baseUrl}/customers`, 1440);
const detailPromise = navigation.context().waitForEvent("page");
await navigation.getByRole("link", { name: "Inspect CUST-HIGH-001" }).click();
const detail = await detailPromise;
await detail.waitForURL("**/app/customer-detail?fixture=CUST-HIGH-001");
await detail.getByRole("heading", { name: "CUST-HIGH-001" }).waitFor();
await capture(detail, "customer-history-inspection-1440.png");
const predictionPromise = detail.context().waitForEvent("page");
await detail
  .getByRole("link", {
    name: "Open CUST-HIGH-001 in Prediction Workspace",
  })
  .click();
const prediction = await predictionPromise;
await prediction.waitForURL("**/app/predict?fixture=CUST-HIGH-001");
await prediction
  .getByRole("heading", { name: /Assess a customer.*s churn risk/ })
  .waitFor();
await prediction.waitForFunction(
  () =>
    document.querySelector('input[aria-label="Customer ID"]')?.value ===
    "CUST-HIGH-001",
);
await prediction.getByRole("button", { name: "Run model prediction" }).click();
await prediction.waitForFunction(() => document.body.innerText.includes("87%"));
await capture(prediction, "prediction-regression-1440.png");
await prediction.close();
await detail.close();
await navigation.close();

console.log("regression:command-center");
const command = await createPage(`${baseUrl}/`, 1440);
await command.getByRole("heading", { name: "Command Center" }).waitFor();
await command.getByText("CUST-HARD-001", { exact: true }).first().waitFor();
await assertNoOverflow(command, "command-center-regression");
await capture(command, "command-center-regression-1440.png");
await command.close();

console.log("customer-history:accessibility-audit");
const auditPage = await createPage(`${baseUrl}/customers`, 1440);
await auditPage.getByRole("heading", { name: "Customer History" }).waitFor();
await auditPage
  .getByRole("textbox", { name: "Search customer history" })
  .focus();
await auditPage.keyboard.press("Tab");
const semanticAudit = await auditPage.evaluate(() => {
  const controls = [
    ...document.querySelectorAll("input,button,a,summary,[role=combobox]"),
  ];
  const unnamed = controls.filter((element) => {
    const style = getComputedStyle(element);
    if (
      element.getClientRects().length === 0 ||
      style.display === "none" ||
      style.visibility === "hidden"
    )
      return false;
    return !(
      element.textContent?.trim() ||
      element.getAttribute("aria-label") ||
      element.getAttribute("aria-labelledby")
    );
  });
  const focusedStyle = getComputedStyle(document.activeElement);
  return {
    title: document.title,
    unnamedInteractiveControls: unnamed.length,
    h1Count: document.querySelectorAll("h1").length,
    tableCount: document.querySelectorAll(".ch-table").length,
    tableColumnHeaders: document.querySelectorAll(".ch-table thead th").length,
    inspectActionCount: [...document.querySelectorAll("a")].filter((a) =>
      a.getAttribute("aria-label")?.startsWith("Inspect CUST-"),
    ).length,
    horizontalOverflow: document.body.scrollWidth > window.innerWidth,
    keyboardFocusVisible:
      focusedStyle.outlineStyle !== "none" &&
      parseFloat(focusedStyle.outlineWidth) >= 2,
  };
});
await auditPage.emulateMedia({ reducedMotion: "reduce" });
const reducedMotion = await auditPage.evaluate(
  () => getComputedStyle(document.documentElement).scrollBehavior === "auto",
);
await auditPage.close();

console.log("customer-detail:accessibility-audit");
const detailAuditPage = await createPage(
  `${baseUrl}/customer-detail?fixture=CUST-HIGH-001`,
  1440,
);
await detailAuditPage.getByRole("heading", { name: "CUST-HIGH-001" }).waitFor();
await detailAuditPage.keyboard.press("Tab");
const detailSemanticAudit = await detailAuditPage.evaluate(() => {
  const controls = [
    ...document.querySelectorAll("input,button,a,summary,[role=combobox]"),
  ];
  const unnamed = controls.filter((element) => {
    const style = getComputedStyle(element);
    if (
      element.getClientRects().length === 0 ||
      style.display === "none" ||
      style.visibility === "hidden"
    )
      return false;
    return !(
      element.textContent?.trim() ||
      element.getAttribute("aria-label") ||
      element.getAttribute("aria-labelledby")
    );
  });
  const focusedStyle = getComputedStyle(document.activeElement);
  return {
    unnamedInteractiveControls: unnamed.length,
    h1Count: document.querySelectorAll("h1").length,
    orderedDriverLists: document.querySelectorAll("ol.cd-drivers").length,
    driverCount: document.querySelectorAll(".cd-driver").length,
    contextSections: document.querySelectorAll(".cd-context section").length,
    riskText:
      document.querySelector(".cd-risk")?.textContent?.includes("HIGH RISK") ??
      false,
    horizontalOverflow: document.body.scrollWidth > window.innerWidth,
    keyboardFocusVisible:
      focusedStyle.outlineStyle !== "none" &&
      parseFloat(focusedStyle.outlineWidth) >= 2,
  };
});
await detailAuditPage.emulateMedia({ reducedMotion: "reduce" });
const detailReducedMotion = await detailAuditPage.evaluate(
  () => getComputedStyle(document.documentElement).scrollBehavior === "auto",
);
await detailAuditPage.close();

console.log("batch:accessibility-audit");
const batchAuditPage = await createPage(`${baseUrl}/batch`, 1440);
await loadDemoBatch(batchAuditPage);
await runDemoBatch(batchAuditPage);
await batchAuditPage.getByRole("combobox", { name: /Dataset source$/ }).focus();
await batchAuditPage.keyboard.press("Tab");
const batchSemanticAudit = await batchAuditPage.evaluate(() => {
  const controls = [
    ...document.querySelectorAll(
      "input,button,a,summary,[role=combobox],[data-testid=stFileUploader]",
    ),
  ];
  const unnamed = controls.filter((element) => {
    const style = getComputedStyle(element);
    if (
      element.getClientRects().length === 0 ||
      style.display === "none" ||
      style.visibility === "hidden"
    )
      return false;
    return !(
      element.textContent?.trim() ||
      element.getAttribute("aria-label") ||
      element.getAttribute("aria-labelledby")
    );
  });
  const focusedStyle = getComputedStyle(document.activeElement);
  return {
    unnamedInteractiveControls: unnamed.length,
    h1Count: document.querySelectorAll("h1").length,
    resultTables: document.querySelectorAll(".bp-results-table table").length,
    resultColumnHeaders: document.querySelectorAll(
      ".bp-results-table thead th",
    ).length,
    summaryItems: document.querySelectorAll(".bp-summary > div").length,
    distributionRows: document.querySelectorAll(".bp-dist-row").length,
    inspectActionCount: [...document.querySelectorAll("button")].filter((button) =>
      button.textContent?.trim().startsWith("Inspect CUST-"),
    ).length,
    riskText:
      document.querySelector(".bp-results-table")?.textContent?.includes("High") ??
      false,
    horizontalOverflow: document.body.scrollWidth > window.innerWidth,
    keyboardFocusVisible:
      focusedStyle.outlineStyle !== "none" &&
      parseFloat(focusedStyle.outlineWidth) >= 2,
  };
});
await batchAuditPage.emulateMedia({ reducedMotion: "reduce" });
const batchReducedMotion = await batchAuditPage.evaluate(
  () => getComputedStyle(document.documentElement).scrollBehavior === "auto",
);
await batchAuditPage.close();

console.log("analytics:accessibility-audit");
const analyticsAuditPage = await createPage(`${baseUrl}/analytics`, 1440);
await analyticsAuditPage
  .getByRole("heading", { name: "Analytics", exact: true })
  .waitFor();
await analyticsAuditPage
  .getByRole("combobox", { name: /Segment breakdown$/ })
  .focus();
const analyticsSemanticAudit = await analyticsAuditPage.evaluate(() => {
  const controls = [
    ...document.querySelectorAll("input,button,a,summary,[role=combobox]"),
  ];
  const unnamed = controls.filter((element) => {
    const style = getComputedStyle(element);
    if (
      element.getClientRects().length === 0 ||
      style.display === "none" ||
      style.visibility === "hidden"
    )
      return false;
    return !(
      element.textContent?.trim() ||
      element.getAttribute("aria-label") ||
      element.getAttribute("aria-labelledby")
    );
  });
  const focusedStyle = getComputedStyle(document.activeElement);
  return {
    unnamedInteractiveControls: unnamed.length,
    h1Count: document.querySelectorAll("h1").length,
    summaryItems: document.querySelectorAll(".an-summary > div").length,
    distributionRows: document.querySelectorAll(".an-bar-row").length,
    volumeRows: document.querySelectorAll(".an-volume-row").length,
    segmentTables: document.querySelectorAll(".an-segment-table table").length,
    segmentColumnHeaders: document.querySelectorAll(
      ".an-segment-table thead th",
    ).length,
    outcomeUnavailable:
      document
        .querySelector(".an-unavailable")
        ?.textContent?.includes("Rate not available") ?? false,
    riskText:
      document
        .querySelector(".an-panel")
        ?.textContent?.includes("Medium / Watch") ?? false,
    horizontalOverflow: document.body.scrollWidth > window.innerWidth,
    keyboardFocusVisible:
      focusedStyle.outlineStyle !== "none" &&
      parseFloat(focusedStyle.outlineWidth) >= 2,
  };
});
await analyticsAuditPage.emulateMedia({ reducedMotion: "reduce" });
const analyticsReducedMotion = await analyticsAuditPage.evaluate(
  () => getComputedStyle(document.documentElement).scrollBehavior === "auto",
);
await analyticsAuditPage.close();

console.log("model:accessibility-audit");
const modelAuditPage = await createPage(`${baseUrl}/model`, 1440);
await modelAuditPage.getByRole("heading", { name: "Model", exact: true }).waitFor();
await modelAuditPage
  .getByRole("link", { name: "Model", exact: true })
  .focus();
const modelSemanticAudit = await modelAuditPage.evaluate(() => {
  const controls = [
    ...document.querySelectorAll("input,button,a,summary,[role=combobox]"),
  ];
  const unnamed = controls.filter((element) => {
    const style = getComputedStyle(element);
    if (
      element.getClientRects().length === 0 ||
      style.display === "none" ||
      style.visibility === "hidden"
    )
      return false;
    return !(
      element.textContent?.trim() ||
      element.getAttribute("aria-label") ||
      element.getAttribute("aria-labelledby")
    );
  });
  const focusedStyle = getComputedStyle(document.activeElement);
  return {
    unnamedInteractiveControls: unnamed.length,
    h1Count: document.querySelectorAll("h1").length,
    statusSections: document.querySelectorAll(".mo-status").length,
    identityItems: document.querySelectorAll(".mo-identity > div").length,
    configurationSections: document.querySelectorAll(
      ".mo-configuration > section",
    ).length,
    candidateTables: document.querySelectorAll(".mo-candidate-table table")
      .length,
    candidateHeaders: document.querySelectorAll(
      ".mo-candidate-table thead th",
    ).length,
    candidateRows: document.querySelectorAll(".mo-candidate-table tbody tr")
      .length,
    boundaryNotes: document.querySelectorAll(".mo-boundary").length,
    unavailableMetrics: (() => {
      const text =
        document.querySelector(".mo-candidate-table")?.textContent ?? "";
      return text.includes("Planned") && text.includes("not trained");
    })(),
    horizontalOverflow: document.body.scrollWidth > window.innerWidth,
    keyboardFocusVisible:
      focusedStyle.outlineStyle !== "none" &&
      parseFloat(focusedStyle.outlineWidth) >= 2,
  };
});
await modelAuditPage.emulateMedia({ reducedMotion: "reduce" });
const modelReducedMotion = await modelAuditPage.evaluate(
  () => getComputedStyle(document.documentElement).scrollBehavior === "auto",
);
await modelAuditPage.close();

console.log("model-explanations:accessibility-audit");
const explanationAuditPage = await createPage(
  `${baseUrl}/model-explanations?fixture=CUST-HIGH-001`,
  1440,
);
await explanationAuditPage
  .getByRole("heading", { name: "Model Explanations", exact: true })
  .waitFor();
await explanationAuditPage
  .getByRole("combobox", { name: /Approved explanation customer$/ })
  .focus();
const explanationSemanticAudit = await explanationAuditPage.evaluate(() => {
  const controls = [
    ...document.querySelectorAll(
      "input,button,a,summary,[role=combobox]",
    ),
  ];
  const unnamed = controls.filter((element) => {
    const style = getComputedStyle(element);
    if (
      element.getClientRects().length === 0 ||
      style.display === "none" ||
      style.visibility === "hidden"
    )
      return false;
    return !(
      element.textContent?.trim() ||
      element.getAttribute("aria-label") ||
      element.getAttribute("aria-labelledby")
    );
  });
  const focusedStyle = getComputedStyle(document.activeElement);
  return {
    unnamedInteractiveControls: unnamed.length,
    h1Count: document.querySelectorAll("h1").length,
    globalLists: document.querySelectorAll(".ex-global-list").length,
    globalDrivers: document.querySelectorAll(".ex-global-driver").length,
    globalTables: document.querySelectorAll(".ex-global-table table").length,
    globalHeaders: document.querySelectorAll(".ex-global-table thead th").length,
    localHeads: document.querySelectorAll(".ex-local-head").length,
    localDrivers: document.querySelectorAll(".ex-local-driver").length,
    technicalDisclosures: document.querySelectorAll(
      ".ex-local-driver details",
    ).length,
    methodologyDisclosures: document.querySelectorAll(".ex-method").length,
    operatorReadouts: document.querySelectorAll(".ex-operator").length,
    directionText:
      document.body.innerText.includes("Higher-risk signal") &&
      document.body.innerText.includes("Demo explanation data"),
    horizontalOverflow: document.body.scrollWidth > window.innerWidth,
    keyboardFocusVisible:
      focusedStyle.outlineStyle !== "none" &&
      parseFloat(focusedStyle.outlineWidth) >= 2,
  };
});
await explanationAuditPage.emulateMedia({ reducedMotion: "reduce" });
const explanationReducedMotion = await explanationAuditPage.evaluate(
  () => getComputedStyle(document.documentElement).scrollBehavior === "auto",
);
await explanationAuditPage.close();

await fs.writeFile(
  path.join(output, "audit.json"),
  JSON.stringify(
    {
      semanticAudit,
      detailSemanticAudit,
      batchSemanticAudit,
      analyticsSemanticAudit,
      modelSemanticAudit,
      explanationSemanticAudit,
      reducedMotion,
      detailReducedMotion,
      batchReducedMotion,
      analyticsReducedMotion,
      modelReducedMotion,
      explanationReducedMotion,
      consoleErrors,
      frameworkBootstrapProbes,
    },
    null,
    2,
  ),
);
await browser.close();

if (consoleErrors.length) {
  throw new Error(`Browser errors detected: ${consoleErrors.join(" | ")}`);
}
if (
  semanticAudit.unnamedInteractiveControls !== 0 ||
  semanticAudit.h1Count !== 1 ||
  semanticAudit.tableCount !== 1 ||
  semanticAudit.tableColumnHeaders !== 9 ||
  semanticAudit.inspectActionCount < 4 ||
  semanticAudit.horizontalOverflow ||
  !semanticAudit.keyboardFocusVisible ||
  !reducedMotion ||
  detailSemanticAudit.unnamedInteractiveControls !== 0 ||
  detailSemanticAudit.h1Count !== 1 ||
  detailSemanticAudit.orderedDriverLists !== 1 ||
  detailSemanticAudit.driverCount !== 3 ||
  detailSemanticAudit.contextSections !== 3 ||
  !detailSemanticAudit.riskText ||
  detailSemanticAudit.horizontalOverflow ||
  !detailSemanticAudit.keyboardFocusVisible ||
  !detailReducedMotion ||
  batchSemanticAudit.unnamedInteractiveControls !== 0 ||
  batchSemanticAudit.h1Count !== 1 ||
  batchSemanticAudit.resultTables !== 1 ||
  batchSemanticAudit.resultColumnHeaders !== 6 ||
  batchSemanticAudit.summaryItems !== 5 ||
  batchSemanticAudit.distributionRows !== 3 ||
  batchSemanticAudit.inspectActionCount < 4 ||
  !batchSemanticAudit.riskText ||
  batchSemanticAudit.horizontalOverflow ||
  !batchSemanticAudit.keyboardFocusVisible ||
  !batchReducedMotion ||
  analyticsSemanticAudit.unnamedInteractiveControls !== 0 ||
  analyticsSemanticAudit.h1Count !== 1 ||
  analyticsSemanticAudit.summaryItems !== 3 ||
  analyticsSemanticAudit.distributionRows !== 3 ||
  analyticsSemanticAudit.volumeRows !== 1 ||
  analyticsSemanticAudit.segmentTables !== 1 ||
  analyticsSemanticAudit.segmentColumnHeaders !== 5 ||
  !analyticsSemanticAudit.outcomeUnavailable ||
  !analyticsSemanticAudit.riskText ||
  analyticsSemanticAudit.horizontalOverflow ||
  !analyticsSemanticAudit.keyboardFocusVisible ||
  !analyticsReducedMotion ||
  modelSemanticAudit.unnamedInteractiveControls !== 0 ||
  modelSemanticAudit.h1Count !== 1 ||
  modelSemanticAudit.statusSections !== 1 ||
  modelSemanticAudit.identityItems !== 5 ||
  modelSemanticAudit.configurationSections !== 2 ||
  modelSemanticAudit.candidateTables !== 1 ||
  modelSemanticAudit.candidateHeaders !== 8 ||
  modelSemanticAudit.candidateRows !== 4 ||
  modelSemanticAudit.boundaryNotes !== 1 ||
  !modelSemanticAudit.unavailableMetrics ||
  modelSemanticAudit.horizontalOverflow ||
  !modelSemanticAudit.keyboardFocusVisible ||
  !modelReducedMotion ||
  explanationSemanticAudit.unnamedInteractiveControls !== 0 ||
  explanationSemanticAudit.h1Count !== 1 ||
  explanationSemanticAudit.globalLists !== 1 ||
  explanationSemanticAudit.globalDrivers !== 5 ||
  explanationSemanticAudit.globalTables !== 1 ||
  explanationSemanticAudit.globalHeaders !== 6 ||
  explanationSemanticAudit.localHeads !== 1 ||
  explanationSemanticAudit.localDrivers !== 3 ||
  explanationSemanticAudit.technicalDisclosures !== 3 ||
  explanationSemanticAudit.methodologyDisclosures !== 1 ||
  explanationSemanticAudit.operatorReadouts !== 1 ||
  !explanationSemanticAudit.directionText ||
  explanationSemanticAudit.horizontalOverflow ||
  !explanationSemanticAudit.keyboardFocusVisible ||
  !explanationReducedMotion
) {
  throw new Error(
    `Accessibility/semantic audit failed: ${JSON.stringify({
      semanticAudit,
      detailSemanticAudit,
      batchSemanticAudit,
      analyticsSemanticAudit,
      modelSemanticAudit,
      explanationSemanticAudit,
      reducedMotion,
      detailReducedMotion,
      batchReducedMotion,
      analyticsReducedMotion,
      modelReducedMotion,
      explanationReducedMotion,
    })}`,
  );
}

console.log(
  JSON.stringify(
    {
      screenshots: 77,
      viewports,
      semanticAudit,
      detailSemanticAudit,
      batchSemanticAudit,
      analyticsSemanticAudit,
      modelSemanticAudit,
      explanationSemanticAudit,
      reducedMotion,
      detailReducedMotion,
      batchReducedMotion,
      analyticsReducedMotion,
      modelReducedMotion,
      explanationReducedMotion,
      consoleErrors: 0,
      ignoredFrameworkBootstrapProbes: frameworkBootstrapProbes.length,
    },
    null,
    2,
  ),
);