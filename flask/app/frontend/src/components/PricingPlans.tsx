import { CheckIcon } from '@heroicons/react/20/solid';

const tiers = [
  {
    name: 'Community',
    id: 'tier-community',
    href: '#',
    price: '$0',
    frequency: '/month',
    description: 'Perfect for developers building with deprecated Spotify APIs',
    features: [
      '10 API calls per month',
      'Drop-in Spotify API replacement',
      'Audio Features API',
      'Audio Analysis API',
      'Basic Recommendations',
      'Community support',
    ],
    mostPopular: false,
  },
  {
    name: 'Pro',
    id: 'tier-pro',
    href: 'https://buy.stripe.com/00g0195Jd2Ry3rq8wB',
    price: '$20',
    frequency: '/month',
    description: 'For professional applications and teams',
    features: [
      '1,500 API calls per month',
      'All Spotify replacement APIs',
      'Advanced Audio Analysis',
      'Enhanced Recommendations',
      'Related Artists API',
      'Featured Playlists API',
      'Priority support',
      'API key management',
    ],
    mostPopular: true,
  },
  {
    name: 'Enterprise',
    id: 'tier-enterprise',
    href: 'https://buy.stripe.com/bIY7tB2x1cs89PO7sy',
    price: '$99',
    frequency: '/month',
    description: 'For large-scale applications',
    features: [
      'Unlimited API calls',
      'Custom endpoints development',
      'Private deployment option',
      'Custom model training',
      'SLA guarantee',
      'Dedicated support',
      'Advanced analytics',
      'White-label option',
    ],
    mostPopular: false,
  },
];

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ');
}

export default function PricingPlans() {
  return (
    <div className="relative bg-gray-900/50 py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="text-base font-semibold leading-7 text-blue-400">Pricing</h2>
          <p className="mt-2 text-4xl font-bold tracking-tight text-white sm:text-5xl">
            Choose the right plan for&nbsp;you
          </p>
        </div>
        <p className="mx-auto mt-6 max-w-2xl text-center text-lg leading-8 text-gray-300">
          Get access to our powerful audio analysis API and start analyzing your music today.
        </p>
        <div className="mt-16 flex justify-center">
          <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
            {tiers.map((tier) => (
              <div
                key={tier.id}
                className={classNames(
                  tier.mostPopular ? 'ring-2 ring-blue-500' : 'ring-1 ring-gray-700',
                  'rounded-3xl p-8 xl:p-10 bg-gray-800/50 backdrop-blur-sm'
                )}
              >
                <div className="flex items-center justify-between gap-x-4">
                  <h3
                    id={tier.id}
                    className={classNames(
                      tier.mostPopular ? 'text-blue-400' : 'text-white',
                      'text-lg font-semibold leading-8'
                    )}
                  >
                    {tier.name}
                  </h3>
                  {tier.mostPopular ? (
                    <p className="rounded-full bg-blue-500/10 px-2.5 py-1 text-xs font-semibold leading-5 text-blue-400">
                      Most popular
                    </p>
                  ) : null}
                </div>
                <p className="mt-4 text-sm leading-6 text-gray-300">{tier.description}</p>
                <p className="mt-6 flex items-baseline gap-x-1">
                  <span className="text-4xl font-bold tracking-tight text-white">{tier.price}</span>
                  <span className="text-sm font-semibold leading-6 text-gray-300">{tier.frequency}</span>
                </p>
                <a
                  href={tier.href}
                  aria-describedby={tier.id}
                  className={classNames(
                    tier.mostPopular
                      ? 'bg-blue-500 text-white shadow-sm hover:bg-blue-400 focus-visible:outline-blue-500'
                      : 'bg-gray-700/50 text-white hover:bg-gray-700 focus-visible:outline-white',
                    'mt-6 block rounded-md py-2 px-3 text-center text-sm font-semibold leading-6 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2'
                  )}
                >
                  Get started
                </a>
                <ul role="list" className="mt-8 space-y-3 text-sm leading-6 text-gray-300">
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex gap-x-3">
                      <CheckIcon className="h-6 w-5 flex-none text-blue-400" aria-hidden="true" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
} 