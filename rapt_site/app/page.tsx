import React from 'react';

import Link from 'next/link';
import { Button } from '@mantine/core';

function Demo() {
  return (
    <Button component={Link} href="/hello">
      Next link button
    </Button>
  );
}

export default function Page() {
    return <div>
        <Demo />
        <h1>Rapt.chat, coming soon!</h1>
    </div> 
}