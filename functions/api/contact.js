const MAX_BODY_BYTES = 32_768;

function text(form, key, maxLength = 500) {
  return String(form.get(key) || '').trim().slice(0, maxLength);
}

function redirect(request, state) {
  const url = new URL('/contact', request.url);
  url.searchParams.set(state, '1');
  return Response.redirect(url.toString(), 303);
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const contentLength = Number(request.headers.get('content-length') || 0);
  if (contentLength > MAX_BODY_BYTES) {
    return new Response('Request too large', { status: 413 });
  }

  const requestUrl = new URL(request.url);
  const origin = request.headers.get('origin');
  if (origin && new URL(origin).hostname !== requestUrl.hostname) {
    return new Response('Invalid origin', { status: 403 });
  }

  let form;
  try {
    form = await request.formData();
  } catch {
    return new Response('Invalid form submission', { status: 400 });
  }

  // Honeypot fields are intentionally accepted but never stored.
  if (text(form, 'company_url', 200)) {
    return redirect(request, 'submitted');
  }

  const startedAt = Number(text(form, 'form_started_at', 20));
  const elapsed = Date.now() - startedAt;
  if (!Number.isFinite(startedAt) || elapsed < 1_000 || elapsed > 86_400_000) {
    return redirect(request, 'error');
  }

  const lead = {
    name: text(form, 'name', 120),
    email: text(form, 'email', 254).toLowerCase(),
    phone: text(form, 'phone', 40),
    company: text(form, 'company', 160),
    website: text(form, 'website', 300),
    projectType: text(form, 'project_type', 80),
    timeline: text(form, 'timeline', 80),
    budget: text(form, 'budget', 80),
    message: text(form, 'message', 4_000),
    sourcePage: text(form, 'source_page', 500),
    referrer: text(form, 'referrer', 500),
    utmSource: text(form, 'utm_source', 200),
    utmMedium: text(form, 'utm_medium', 200),
    utmCampaign: text(form, 'utm_campaign', 200),
    utmTerm: text(form, 'utm_term', 300),
    utmContent: text(form, 'utm_content', 300),
    gclid: text(form, 'gclid', 300),
  };

  const validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(lead.email);
  if (!lead.name || !validEmail || !lead.projectType || lead.message.length < 10) {
    return redirect(request, 'error');
  }

  try {
    await env.LEADS_DB.prepare(`
      INSERT INTO leads (
        name, email, phone, company, website, project_type, timeline, budget,
        message, source_page, referrer, utm_source, utm_medium, utm_campaign,
        utm_term, utm_content, gclid, country, cf_ray
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(
      lead.name,
      lead.email,
      lead.phone,
      lead.company,
      lead.website,
      lead.projectType,
      lead.timeline,
      lead.budget,
      lead.message,
      lead.sourcePage,
      lead.referrer,
      lead.utmSource,
      lead.utmMedium,
      lead.utmCampaign,
      lead.utmTerm,
      lead.utmContent,
      lead.gclid,
      request.cf?.country || '',
      request.headers.get('cf-ray') || ''
    ).run();
  } catch (error) {
    console.error('Lead storage failed', error);
    return redirect(request, 'error');
  }

  return redirect(request, 'submitted');
}

export function onRequest() {
  return new Response('Method not allowed', {
    status: 405,
    headers: { Allow: 'POST' },
  });
}
